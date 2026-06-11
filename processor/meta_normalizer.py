"""MetaNormalizer — 封面 metadata 自癒對齊飛輪（META-NORM C2）。

依 `.claude-logs/baton/2026-06-11_META-NORM_..._tasks.md` §8 C2 + plan v1.2 §2 U3/U4
（繼承 DOMAIN-NORM C2 範式：快取 → LLM 比對 → 動態註冊 → 寫回）。

職責：把 P1 Vision 開放抽取之高自由度封面欄名（raw_key、欄名自定），經二次 LLM
比對既有 MetaField 全集後收斂至穩定 canonical_key（防 key drift：課程/course/
class_code → course），並動態註冊冷門欄位 + i18n 標籤提案。

對齊流程（plan U3）：
  reserved 命中（title/authors/venue/doi）→ 直接映回凍結合約欄、不入登記表、不問 LLM（BS1）
  泛用詞黑名單（date/name/title…）→ 不查快取、每次過 LLM 帶 context（Q9/BS3 防跨件污染）
  非黑名單 → ① 快取查 MetaFieldAlias → 命中即回
            ② 未命中 → LLM 比對既有 canonical 全集（temp=0、交易外）→ 映既有 / 提新欄 + label
            ③ on_conflict_do_nothing 動態註冊 MetaField（含 label）+ 寫回 alias 快取

鐵律（database/logging SOP）：
  - LLM 呼叫一律在 DB 交易（session.begin()）外，取得結果才開極短交易寫表。
  - 寫入 on_conflict_do_nothing 冪等，防併發 IntegrityError（BS5）。
  - 全程 try/except，任何失敗降級回 raw 欄名原樣（logger.error exc_info=True），不阻斷 Pipeline。

公開入口 `normalize_fields` 受 settings.LLM_USE_META_NORM 旗標控制（False 預設→直回原樣）。
"""
from __future__ import annotations

import json
import logging
import re
from typing import Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from db import SessionLocal
from llm.client import LLMClient
from models import MetaField, MetaFieldAlias
import settings

logger = logging.getLogger(__name__)

# === [META-NORM C2 START] ===
# reserved：凍結合約 IngestionMetadataSpec 已擁有之欄（BS1）——直接映回合約欄、不入登記表、
# 不問 LLM、不寫旁路（避免雙重表示）。回傳之 canonical 以 _RESERVED_PREFIX 標記、交 P1 回填合約。
_RESERVED_PREFIX = "__reserved__:"
_RESERVED_MAPPING = {
    "title": "title", "標題": "title", "cover_title": "title", "主標題": "title",
    "author": "authors", "authors": "authors", "作者": "authors", "講者": "authors",
    "presenter": "authors", "presenters": "authors",
    "venue": "venue", "期刊": "venue", "發表地點": "venue", "conference": "venue",
    "doi": "doi",
}

# 泛用模糊單字黑名單（Q9/BS3）：語境相依性高（date=publish vs due），不寫 alias 快取、
# 每次過 LLM 帶 context 判定，防一次映射釘死後跨文檔誤路由。
_GENERIC_KEYS = {
    "date", "time", "name", "title", "class", "type",
    "status", "id", "no", "code", "user",
}

# 比對 System Instruction：LLM 將自提欄名與既有 canonical 全集比對、映既有或提新欄 + label。
_META_ALIGN_SYSTEM_PROMPT = (
    "你是文件元數據欄位標準化專家。使用者提供一個『原始欄名』（可能中英任意命名）、其值、"
    "可選的封面上下文，以及『既有標準欄位清單』。請判斷該原始欄名應對應哪個標準欄位：\n"
    "嚴格規則：\n"
    "1. 只回傳一行 JSON：{\"canonical\":\"...\",\"label_zh\":\"...\",\"label_en\":\"...\"}。\n"
    "2. 若與既有清單某欄『語意明確同義』→ canonical 用該既有 key、label 留空（沿用既有）。\n"
    "3. 僅在明確同義時才合併；語意有別（如 發布日 vs 截止日）一律視為新欄、給新 canonical。\n"
    "4. 新欄 canonical 用簡短英文 snake_case（如 course/instructor）、並提供 label_zh/label_en。\n"
    "5. 完全無法判斷時 canonical 回原始欄名的 snake_case 形。\n"
    "不要輸出任何其他解釋、前綴或標點。"
)


class MetaNormalizer:
    """封面 metadata 欄名自癒對齊器（繼承 DomainNormalizer 範式）。"""

    def __init__(self, llm=None, session_factory=None):
        # 依賴注入：測試可傳 mock llm / in-memory session_factory。
        self.llm = llm if llm is not None else LLMClient.get_instance()
        self._session_factory = session_factory if session_factory is not None else SessionLocal
        self.logger = logger

    # ------------------------------------------------------------------ #
    # 輔助
    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize_key(raw_key: str) -> str:
        """raw 欄名正規化為穩定快取鍵（lowercase + strip）。"""
        return (raw_key or "").strip().lower()

    @staticmethod
    def _parse_llm_result(text: str) -> Optional[Tuple[str, str, str]]:
        """解析 LLM 回傳 JSON {canonical,label_zh,label_en}；格式不符回 None。"""
        if not text:
            return None
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return None
        try:
            d = json.loads(m.group(0))
        except (ValueError, TypeError):
            return None
        canonical = (d.get("canonical") or "").strip()
        if not canonical:
            return None
        # canonical 收斂為 snake_case 安全鍵
        canonical = re.sub(r"\s+", "_", canonical).lower()
        return canonical, (d.get("label_zh") or "").strip(), (d.get("label_en") or "").strip()

    # ------------------------------------------------------------------ #
    # ① 快取查（read-only、極短 session）
    # ------------------------------------------------------------------ #
    def _cache_lookup(self, norm_key: str) -> Optional[str]:
        with self._session_factory() as session:
            row = session.get(MetaFieldAlias, norm_key)
            return row.canonical_key if row is not None else None

    def _existing_canonicals(self) -> list:
        """讀既有 MetaField canonical 全集（供 LLM 比對；read-only）。"""
        with self._session_factory() as session:
            return list(session.execute(select(MetaField.canonical_key)).scalars().all())

    # ------------------------------------------------------------------ #
    # ② LLM 比對（**交易外**、不持有 DB session）
    # ------------------------------------------------------------------ #
    def _llm_classify(
        self, raw_key: str, value: str, context: str, existing: list
    ) -> Optional[Tuple[str, str, str]]:
        user_parts = [
            f"原始欄名：{raw_key}",
            f"值：{(value or '')[:200]}",
            f"既有標準欄位清單：{', '.join(existing) if existing else '（空）'}",
        ]
        if context:
            user_parts.append(f"封面上下文：{context[:1000]}")
        messages = [
            {"role": "system", "content": _META_ALIGN_SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(user_parts)},
        ]
        result = self.llm.chat(
            messages=messages, temperature=0.0, stream=False,
            model=settings.LLM_DOMAIN_MODEL,
        )
        parsed = self._parse_llm_result(result or "")
        self.logger.info("[meta-norm] LLM 比對 raw=%r → %r", raw_key, parsed)
        return parsed

    # ------------------------------------------------------------------ #
    # ③ 動態註冊 MetaField + 寫回 MetaFieldAlias（極短交易、冪等）
    # ------------------------------------------------------------------ #
    def _register_and_cache(
        self, norm_key: str, canonical: str, label_zh: str, label_en: str,
        *, write_alias: bool,
    ) -> None:
        with self._session_factory() as session:
            with session.begin():
                # 動態註冊新 canonical（label 缺則以 canonical 兜底；BS4）。
                session.execute(
                    sqlite_insert(MetaField)
                    .values(
                        canonical_key=canonical,
                        label_zh=label_zh or canonical,
                        label_en=label_en or canonical,
                        category="cover", source="auto_register", sort_weight=100,
                    )
                    .on_conflict_do_nothing(index_elements=["canonical_key"])
                )
                # 黑名單泛用詞不寫 alias（Q9/BS3）；其餘冪等寫回快取（BS5）。
                if write_alias:
                    session.execute(
                        sqlite_insert(MetaFieldAlias)
                        .values(raw_key=norm_key, canonical_key=canonical)
                        .on_conflict_do_nothing(index_elements=["raw_key"])
                    )

    # ------------------------------------------------------------------ #
    # 主流程：raw_fields → canonical dict（reserved 標記交 P1 回填合約）
    # ------------------------------------------------------------------ #
    def normalize(self, raw_fields: Dict[str, str], context: str = "") -> Dict[str, str]:
        out: Dict[str, str] = {}
        for raw_key, value in (raw_fields or {}).items():
            try:
                norm = self._normalize_key(raw_key)
                if not norm:
                    continue
                # reserved：映回合約欄、不入庫不問 LLM（BS1）
                if norm in _RESERVED_MAPPING:
                    out[f"{_RESERVED_PREFIX}{_RESERVED_MAPPING[norm]}"] = value
                    continue
                is_generic = norm in _GENERIC_KEYS
                # 非黑名單先查快取
                canonical = None if is_generic else self._cache_lookup(norm)
                if canonical is None:
                    parsed = self._llm_classify(norm, value, context, self._existing_canonicals())
                    if parsed is None:
                        out[raw_key] = value          # LLM 無解 → 原樣保留（不阻斷）
                        continue
                    canonical, label_zh, label_en = parsed
                    # 黑名單不寫 alias；其餘寫回快取
                    self._register_and_cache(
                        norm, canonical, label_zh, label_en, write_alias=not is_generic)
                out[canonical] = value
            except Exception:  # noqa: BLE001 — 單欄失敗降級原樣、不阻斷 Pipeline
                self.logger.error(
                    "[meta-norm] 欄位對齊失敗，降級原樣 raw=%r", raw_key, exc_info=True)
                out[raw_key] = value
        return out


# 模組級單例（旗標啟用時才實例化、避免 import 期建 LLMClient/DB 連線）。
_normalizer_singleton: Optional[MetaNormalizer] = None


def _get_normalizer() -> MetaNormalizer:
    global _normalizer_singleton
    if _normalizer_singleton is None:
        _normalizer_singleton = MetaNormalizer()
    return _normalizer_singleton


def normalize_fields(raw_fields: Dict[str, str], context: str = "") -> Dict[str, str]:
    """MetaNormalizer 單一公開入口。

    熱插拔旗標 settings.LLM_USE_META_NORM：
      - False（預設）→ 直接回傳 raw_fields 原樣，**不查 DB、不呼 LLM**，零風險。
      - True → 委派 MetaNormalizer.normalize（快取→LLM 比對→動態註冊→寫回，失敗降級原樣）。
    回傳之 key 含 reserved 標記者（`__reserved__:authors` 等）由 P1 回填凍結合約、其餘走旁路。
    """
    if not settings.LLM_USE_META_NORM:
        return dict(raw_fields or {})
    return _get_normalizer().normalize(raw_fields, context)
# === [META-NORM C2 END] ===

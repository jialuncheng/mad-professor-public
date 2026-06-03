"""DomainNormalizer — 領域標準化對齊器核心（DOMAIN-NORM C2）。

依 `.claude-logs/baton/2026-06-01_DOMAIN-NORM_領域標準化對齊器_tasks.md` §8 C2
+ plan v2 §2 U1/U2。

職責：把 `DomainDetector.detect` 產出的高自由度 raw 領域短句，收斂成穩定可查詢的
LCC（Library of Congress Classification）主類代碼，並動態註冊冷門領域空間。

對齊流程（plan v2 U1+U2）：
  ① 快取查 DomainMapping（raw lowercase+strip 為鍵）→ 命中即回（0ms、零 API）
  ② 未命中 → LLM 內容判定（cheap model、temperature=0.0、依 context_text 技能而非文件類型）
  ③ 查 / 動態註冊 Domains（INSERT OR IGNORE、**不塞單字**，與 GLOSSARY-CORE 物理隔離）
  ④ 寫回 DomainMapping
  ⑤ 回 LCCCode

鐵律：
  - **LLM/外部 API 呼叫一律在 DB 交易（session.begin()）之外**，取得代碼後才開極短交易
    寫表，避免 SQLite `database is locked`（database SOP 原則 2）。
  - 寫入用 INSERT OR IGNORE（on_conflict_do_nothing）冪等，防併發 IntegrityError。
  - 全程 try/except，任何失敗一律降級回 DEFAULT_LCC（"general"），不阻斷 Pipeline。

本模組於 C2 僅建核心類；對外公開入口 `normalize_to_lcc` 與 feature flag
（LLM_USE_GLOSSARY_ALIGN）屬 C3。
"""
from __future__ import annotations

import logging
import re
from typing import Optional, Tuple

from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from db import SessionLocal
from llm.client import LLMClient
from models import DomainMapping, Domains
import settings

logger = logging.getLogger(__name__)

# 型別別名：LCC 主類代碼（1-3 個大寫英文字母，如 "QA"/"HF"/"QE"）。
LCCCode = str

# 降級哨兵：任何判定失敗 / 資訊不足一律回此值（plan §7 Q1）。
DEFAULT_LCC: LCCCode = "general"

# LCC 代碼格式：1-3 個英文字母（plan §7 Q2）。
_LCC_RE = re.compile(r"^[A-Za-z]{1,3}$")

# 對齊器 System Instruction：定義 LCC 收斂規則（內容判定、履歷按技能而非文件類型）。
_ALIGN_SYSTEM_PROMPT = (
    "你是圖書館分類專家。根據使用者提供的『文件領域描述』與（可選的）內文摘要，"
    "判斷其最貼切的 Library of Congress Classification（LCC）主類，並回傳代碼與英文名稱。\n"
    "嚴格規則：\n"
    "1. 只回傳一行，格式為『CODE|Name』（半形直線分隔），例：『QA|Mathematics』。\n"
    "2. CODE 必須是 1-3 個大寫英文字母的標準 LCC 主類/次類代碼，不得包含數字或標點。\n"
    "3. 履歷、個人簡介等文件，必須依其『實質專業技能領域』分類"
    "（例：行銷／社群投放→HF、軟體工程／AI→QA），嚴禁歸類為『resume』這類文件類型。\n"
    "4. 冷門領域亦須給出最接近的 LCC 主類（例：古生物學→QE）。\n"
    "5. 完全無法判斷時，只回傳『general|General』。\n"
    "不要輸出任何其他解釋、前綴或標點。"
)


class DomainNormalizer:
    """領域標準化對齊器：raw 領域短句 → 穩定 LCC 代碼（含動態註冊 + 快取）。"""

    def __init__(self, llm=None, session_factory=None):
        # 依賴注入：測試可傳 mock llm / in-memory session_factory。
        self.llm = llm if llm is not None else LLMClient.get_instance()
        self._session_factory = session_factory if session_factory is not None else SessionLocal
        self.logger = logger

    # ------------------------------------------------------------------ #
    # 輔助
    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize_key(raw_domain: str) -> str:
        """raw 領域短句正規化為穩定快取鍵（lowercase + strip）。"""
        return (raw_domain or "").strip().lower()

    @staticmethod
    def _parse_llm_result(text: str) -> Optional[Tuple[LCCCode, str]]:
        """解析 LLM 回傳『CODE|Name』；格式不符回 None。"""
        if not text:
            return None
        line = text.strip().splitlines()[0].strip()
        if "|" not in line:
            return None
        code_part, _, name_part = line.partition("|")
        code = code_part.strip().upper()
        name = name_part.strip()
        if not _LCC_RE.match(code) or not name:
            return None
        return code, name

    # ------------------------------------------------------------------ #
    # ① 快取查（read-only、極短 session）
    # ------------------------------------------------------------------ #
    def _cache_lookup(self, raw_key: str) -> Optional[LCCCode]:
        with self._session_factory() as session:
            row = session.get(DomainMapping, raw_key)
            return row.lcc_code if row is not None else None

    # ------------------------------------------------------------------ #
    # ② LLM 內容判定（**交易外**、不持有 DB session）
    # ------------------------------------------------------------------ #
    def _llm_classify(
        self, raw_domain: str, context_text: Optional[str]
    ) -> Optional[Tuple[LCCCode, str]]:
        user_parts = [f"文件領域描述：{raw_domain}"]
        if context_text:
            user_parts.append(f"內文摘要：{context_text[:2000]}")
        messages = [
            {"role": "system", "content": _ALIGN_SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(user_parts)},
        ]
        # temperature=0.0：分類任務需確定性；stream=False：短回應一次取回。
        result = self.llm.chat(
            messages=messages,
            temperature=0.0,
            stream=False,
            model=settings.LLM_DOMAIN_MODEL,
        )
        parsed = self._parse_llm_result(result or "")
        self.logger.info(
            "[domain-norm] LLM 判定 raw=%r → %r", raw_domain, parsed
        )
        return parsed

    # ------------------------------------------------------------------ #
    # ③ + ④ 動態註冊 Domains + 寫回 DomainMapping（極短交易、冪等 upsert）
    # ------------------------------------------------------------------ #
    def _register_and_cache(self, raw_key: str, lcc: LCCCode, name: str) -> None:
        with self._session_factory() as session:
            # session.begin()：成功自動 commit、失敗自動 rollback（database SOP 原則 1）。
            with session.begin():
                # INSERT OR IGNORE：領域空間冪等註冊（不塞單字、與 GLOSSARY-CORE 隔離）。
                session.execute(
                    sqlite_insert(Domains)
                    .values(lcc_code=lcc, name=name)
                    .on_conflict_do_nothing(index_elements=["lcc_code"])
                )
                # INSERT OR IGNORE：快取冪等寫回（併發同 raw 不報 IntegrityError）。
                session.execute(
                    sqlite_insert(DomainMapping)
                    .values(raw_key=raw_key, lcc_code=lcc)
                    .on_conflict_do_nothing(index_elements=["raw_key"])
                )

    # ------------------------------------------------------------------ #
    # 主流程（C2 內部入口；C3 的 normalize_to_lcc 會包旗標後委派此處）
    # ------------------------------------------------------------------ #
    def normalize(
        self, raw_domain: str, context_text: Optional[str] = None
    ) -> LCCCode:
        """raw 領域短句 → LCC 代碼；任何失敗降級 DEFAULT_LCC（不阻斷）。"""
        try:
            raw_key = self._normalize_key(raw_domain)
            if not raw_key:
                return DEFAULT_LCC

            # ① 快取命中即回（0ms、零 API）
            cached = self._cache_lookup(raw_key)
            if cached:
                self.logger.info("[domain-norm] 快取命中 raw=%r → %s", raw_domain, cached)
                return cached

            # ② LLM 內容判定（**交易外**）
            parsed = self._llm_classify(raw_domain, context_text)
            if parsed is None:
                self.logger.info(
                    "[domain-norm] LLM 無有效判定，降級 raw=%r → %s",
                    raw_domain, DEFAULT_LCC,
                )
                return DEFAULT_LCC
            lcc, name = parsed

            # ③ + ④ 動態註冊 + 寫回（取得代碼後才開極短交易）
            self._register_and_cache(raw_key, lcc, name)
            self.logger.info(
                "[domain-norm] 註冊+快取 raw=%r → %s (%s)", raw_domain, lcc, name
            )
            return lcc
        except Exception:
            # ⑤ 任何異常一律降級，不阻斷 Pipeline（logging SOP：exc_info=True）。
            self.logger.error(
                "[domain-norm] 對齊失敗，降級 raw=%r → %s",
                raw_domain, DEFAULT_LCC, exc_info=True,
            )
            return DEFAULT_LCC

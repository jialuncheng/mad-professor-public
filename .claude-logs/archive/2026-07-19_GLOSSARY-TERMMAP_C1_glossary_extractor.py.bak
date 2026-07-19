"""GlossaryManager — 中央領域術語庫核心（GLOSSARY-CORE C2）。

依 `.claude-logs/baton/2026-06-01_GLOSSARY-CORE_中央領域術語庫_tasks.md` §8 C2
+ plan v2 §2 U2。對齊 DOMAIN-NORM C2（processor/domain_normalizer.py）的依賴注入 +
交易邊界 + 冪等 upsert pattern。

職責：
  - 級聯優先權查詢（U2）：`WHERE domain IN (文獻 LCC, 'general')`，記憶體中**專屬 LCC 覆寫 general**。
  - LLM 術語提取（U3 飛輪）：從譯文上下文抽取「原文術語 → 繁中譯詞」對。
  - 冪等回填：`INSERT OR IGNORE`（on_conflict_do_nothing）寫回 `GlobalGlossary`。

鐵律（database SOP 原則 2、對齊 DOMAIN-NORM C2）：
  - **LLM `extract_terms` 一律在 DB 交易（session.begin()）之外**，取得術語後才開極短交易寫表，
    避免 SQLite `database is locked`。
  - 寫入用 `on_conflict_do_nothing` 冪等，防併發 IntegrityError（聯合唯一約束）。
  - 全程 try/except，任何失敗不阻斷上游 Pipeline（回空字典 / 空清單）。

本模組於 C2 僅建核心類；translate 注入（C3）/ Chat 注入（C4）/ CLI（C5）為下游接線。
"""
from __future__ import annotations

import json
import logging
import re
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from db import SessionLocal
from llm.client import LLMClient
from models import GlobalGlossary
import settings

logger = logging.getLogger(__name__)

# 通用領域層（級聯查詢的 fallback 層；專屬 LCC 優先權高於此）。
GENERAL_DOMAIN = "general"

# 術語提取 System Instruction：抽取領域專有名詞的原文 + 繁中譯詞。
_EXTRACT_SYSTEM_PROMPT = (
    "你是專業術語抽取器。從使用者提供的『原文片段』與『繁體中文譯文片段』中，"
    "抽取領域專有名詞（人名、地名、技術術語、品種名、專有概念）的對照。\n"
    "嚴格規則：\n"
    "1. 只輸出 JSON 陣列，每元素為 {\"original\": \"原文術語\", \"translation\": \"繁中譯詞\"}。\n"
    "2. 只收錄『專有名詞 / 領域術語』，排除一般詞彙、連接詞、常見動詞。\n"
    "3. 譯詞必須與譯文片段實際採用的譯法一致。\n"
    "4. 無可抽取術語時輸出空陣列 []。\n"
    "不要輸出任何解釋或 JSON 以外的內容。"
)


class GlossaryManager:
    """中央術語庫管理器：級聯查詢 + LLM 術語提取 + 冪等回填。"""

    def __init__(self, llm=None, session_factory=None):
        # 依賴注入：測試可傳 mock llm / in-memory session_factory（對齊 DomainNormalizer）。
        self.llm = llm if llm is not None else None  # 惰性：query 不需 LLM，extract 才建
        self._session_factory = session_factory if session_factory is not None else SessionLocal
        self.logger = logger

    def _get_llm(self):
        if self.llm is None:
            self.llm = LLMClient.get_instance()
        return self.llm

    # ------------------------------------------------------------------ #
    # 輔助
    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize_key(term: str) -> str:
        """原文術語正規化為穩定查詢/寫入鍵（lowercase + strip）。"""
        return (term or "").strip().lower()

    # ------------------------------------------------------------------ #
    # U2 級聯優先權查詢（read-only、極短 session；專屬 LCC 覆寫 general）
    # ------------------------------------------------------------------ #
    def query_cascade(
        self, source_lang: str, target_lang: str, domain: str
    ) -> Dict[str, str]:
        """級聯查詢術語表：`domain IN (domain, 'general')`，回 {term_key: translation}。

        記憶體合併順序：先填 general，再以專屬 domain 覆寫 → 專屬譯法優先。
        domain 為 'general' 或空時退化為僅查 general。任何失敗回空字典（不阻斷）。
        """
        try:
            domains = [GENERAL_DOMAIN]
            if domain and domain != GENERAL_DOMAIN:
                domains.append(domain)

            with self._session_factory() as session:
                stmt = select(GlobalGlossary).where(
                    GlobalGlossary.source_lang == source_lang,
                    GlobalGlossary.target_lang == target_lang,
                    GlobalGlossary.domain.in_(domains),
                )
                rows = session.execute(stmt).scalars().all()

            # general 先填、專屬 domain 後覆寫（dict 後寫覆蓋前寫）
            general_map: Dict[str, str] = {}
            specific_map: Dict[str, str] = {}
            for r in rows:
                if r.domain == domain and domain != GENERAL_DOMAIN:
                    specific_map[r.term_key] = r.translation
                else:
                    general_map[r.term_key] = r.translation
            merged = {**general_map, **specific_map}
            self.logger.info(
                "[glossary] 級聯查詢 domain=%r general=%d specific=%d → merged=%d",
                domain, len(general_map), len(specific_map), len(merged),
            )
            return merged
        except Exception:
            self.logger.error(
                "[glossary] 級聯查詢失敗 domain=%r → 回空字典", domain, exc_info=True
            )
            return {}

    # ------------------------------------------------------------------ #
    # LLM 術語提取（**交易外**、不持有 DB session）
    # ------------------------------------------------------------------ #
    def extract_terms(
        self, source_text: str, translated_text: str,
        source_lang: str, target_lang: str, domain: str,
    ) -> List[Tuple[str, str]]:
        """LLM 抽取「原文術語 → 繁中譯詞」對；失敗回空清單（不阻斷）。"""
        try:
            user = (
                f"原文片段（{source_lang}）：\n{source_text[:4000]}\n\n"
                f"繁中譯文片段（{target_lang}）：\n{translated_text[:4000]}"
            )
            messages = [
                {"role": "system", "content": _EXTRACT_SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ]
            # temperature=0.0：抽取任務需確定性；stream=False：一次取回。
            result = self._get_llm().chat(
                messages=messages, temperature=0.0, stream=False,
                model=settings.LLM_DOMAIN_MODEL,
            )
            pairs = self._parse_extract_result(result or "")
            self.logger.info(
                "[glossary] LLM 提取 domain=%r → %d 術語", domain, len(pairs)
            )
            return pairs
        except Exception:
            self.logger.error(
                "[glossary] LLM 術語提取失敗 domain=%r → 回空清單", domain, exc_info=True
            )
            return []

    @staticmethod
    def _parse_extract_result(text: str) -> List[Tuple[str, str]]:
        """解析 LLM 回傳 JSON 陣列 [{original, translation}]；容錯 code fence。"""
        if not text:
            return []
        s = text.strip()
        # 去除可能的 ```json fence
        s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.MULTILINE).strip()
        try:
            data = json.loads(s)
        except (json.JSONDecodeError, ValueError):
            return []
        pairs: List[Tuple[str, str]] = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    orig = (item.get("original") or "").strip()
                    trans = (item.get("translation") or "").strip()
                    if orig and trans:
                        pairs.append((orig, trans))
        return pairs

    # ------------------------------------------------------------------ #
    # 冪等回填（取得術語後才開極短交易、INSERT OR IGNORE）
    # ------------------------------------------------------------------ #
    def upsert_terms(
        self, pairs: List[Tuple[str, str]],
        source_lang: str, target_lang: str, domain: str,
        source: str = "auto_extract",
    ) -> int:
        """將術語對冪等寫回 GlobalGlossary；回實際嘗試寫入筆數。失敗不阻斷。"""
        if not pairs:
            return 0
        try:
            domain = domain or GENERAL_DOMAIN
            values = []
            seen = set()
            for original, translation in pairs:
                key = self._normalize_key(original)
                if not key or key in seen:
                    continue
                seen.add(key)
                values.append({
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "term_key": key,
                    "original_term": original.strip(),
                    "translation": translation.strip(),
                    "domain": domain,
                    "source": source,
                })
            if not values:
                return 0
            with self._session_factory() as session:
                # session.begin()：成功自動 commit、失敗自動 rollback（database SOP 原則 1）。
                with session.begin():
                    # INSERT OR IGNORE：併發/重複同 (lang,term,domain) 冪等（聯合唯一約束）。
                    session.execute(
                        sqlite_insert(GlobalGlossary)
                        .values(values)
                        .on_conflict_do_nothing(
                            index_elements=["source_lang", "target_lang", "term_key", "domain"]
                        )
                    )
            self.logger.info(
                "[glossary] 回填 domain=%r 嘗試寫入 %d 術語（重複自動略過）", domain, len(values)
            )
            return len(values)
        except Exception:
            self.logger.error(
                "[glossary] 術語回填失敗 domain=%r → 略過不阻斷", domain, exc_info=True
            )
            return 0

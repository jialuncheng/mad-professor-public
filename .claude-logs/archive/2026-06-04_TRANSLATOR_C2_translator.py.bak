"""Translator 雙模式原子翻譯器（TRANSLATOR C1：合約與上下文模型）。

依 `.claude-logs/baton/2026-06-04_TRANSLATOR_雙模式原子翻譯器_tasks_v1.md` §8 C1
+ plan v10 §2 U1 + PIPE-SPEC §1.2.3 v3。

本檔為 PIPE 大改版三大共用真理源之一「Translator」的型別安全上下文與雙模式列舉。
InjectionContext / TranslateMode **定義於此**（非 pipelines/contracts.py——後者純為四份
Phase 交接合約、物理隔離 doc_type 業務細節，維持 PIPE-CORE 範疇潔癖）。

C1 僅交付合約與 Context 模型；Prompt Engine（C2）/ 雙模式路由與 thinking_config（C3）/
分行容錯與測試（C4）為後續 Commit。
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class TranslateMode(str, Enum):
    """翻譯雙模式（對齊 PIPE-SPEC §1.2.3 / model_recommendations.md §1.1）。

    - NORMAL：降本提速，用於大量正文段落（thinking_budget=0、不啟用思考）。
    - DEEP_THINK：品質優先，用於標題/大綱/摘要（經 thinking_config 啟用思考預算）。
    """

    NORMAL = "normal"
    DEEP_THINK = "deep_think"


class InjectionContext(BaseModel):
    """Translator 逐次注入的型別安全上下文（凍結合約，逐字對齊 PIPE-SPEC §1.2.3 v3）。

    `ConfigDict(frozen=True, extra="forbid")`：不可變 + 拒絕未定義欄位混入。
    承載「文件級脈絡」；`text_type`（本次呼叫屬性）為 translate() 獨立參數、不入此合約。
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    lcc: str  # 標準 LCC 一級分類碼（必填，來自 DOMAIN-NORM normalize_to_lcc）
    glossary: Dict[str, str]  # 凍結最終 Glossary（必填，來自 GLOSSARY-CORE 雙層融合；{term_key: translation}）
    zh_summary: Optional[str] = None  # 中文上下文摘要（依管線：全文宏觀摘要 or 逐章故事板）
    preceding: Optional[str] = None  # 段落級前文參考（Sliding Window 語意）
    constraints: List[str] = []  # 額外自訂約束條件（人名不翻規則等文字級約束）
    domain_name: Optional[str] = None  # P2 預解析的 LCC 領域英文名（=Domains.name，例 "Mathematics"）；Translator 直讀、零 DB
    doc_type: Optional[str] = None  # 文件文體類型（academic/book/slides/...，用於套用對應 Style Hints）

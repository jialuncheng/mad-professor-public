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

import logging
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict

import settings

# === [TRANSLATOR C2 START] ===
# 翻譯提示詞檔路徑（對齊既有 translate_processor.py；caption 為 TRANSLATOR C2 新增交付物）
TITLE_TRANSLATE_PROMPT_PATH = "prompt/translate/title_translate_prompt.txt"
CONTENT_TRANSLATE_PROMPT_PATH = "prompt/translate/content_translate_prompt.txt"
CAPTION_TRANSLATE_PROMPT_PATH = "prompt/translate/caption_translate_prompt.txt"

# 文體風格暗示（七文體，逐字對齊既有 translate_processor.py style_hints）
_STYLE_HINTS = {
    "academic": "文件為學術論文，請使用正式學術用語，保留英文專有名詞與縮寫。",
    "book": "文件為書籍，請使用流暢自然的書面語，保留專有名詞。",
    "technical": "文件為技術文件，請使用精確的技術術語，保留英文技術詞彙。",
    "slides": "文件為簡報投影片，請保持簡潔的條列式風格，勿過度詮釋。",
    "news": "文件為新聞文章，請使用流暢自然的新聞文體，不要過於學術化。",
    "web": "文件為網頁文章，請使用自然口語化的繁體中文。",
    "resume": "文件為個人履歷（CV），請使用正式商務中文，職稱、公司名、技術名詞保留原文。",
}
# === [TRANSLATOR C2 END] ===


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


# === [TRANSLATOR C2 START] ===
class Translator:
    """雙模式原子翻譯器（C2：Prompt Engine 提示詞與約束動態注入）。

    C2 交付系統/用戶提示詞拼接（純函式、零 DB）；公開 `translate()` 的雙模式 chat 路由
    與 thinking_config 受控擴充屬 C3、分行容錯與測試屬 C4。
    """

    def __init__(self, llm=None):
        # 依賴注入：測試可傳 mock LLM。實際 chat 呼叫於 C3 接線。
        self.llm = llm
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @staticmethod
    def _read_file(filepath: str) -> str:
        """讀取提示詞檔；失敗回空字串（對齊既有 translate_processor 容錯）。"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            logging.getLogger(__name__).warning("讀取提示詞檔失敗: %s", filepath)
            return ""

    # ------------------------------------------------------------------ #
    # 系統提示詞拼接（plan U2：五步）
    # ------------------------------------------------------------------ #
    def _build_system_prompt(self, ctx: "InjectionContext", text_type: str = "content") -> str:
        # ① 底層提示詞載入（text_type 路由）
        if text_type == "title":
            system_prompt = self._read_file(TITLE_TRANSLATE_PROMPT_PATH)
        elif text_type == "caption":
            system_prompt = self._read_file(CAPTION_TRANSLATE_PROMPT_PATH)
        else:  # content / abstract
            system_prompt = self._read_file(CONTENT_TRANSLATE_PROMPT_PATH)

        # ② 文體風格暗示（依 ctx.doc_type，預設 academic）
        hint = _STYLE_HINTS.get(ctx.doc_type or "academic", "")
        if hint:
            system_prompt = system_prompt + "\n\n" + hint

        # ③ LCC 領域名稱注入（讀 ctx.domain_name、零 DB；gated 旗標）
        if settings.LLM_USE_GLOSSARY_ALIGN:
            domain_name = ctx.domain_name or ctx.lcc  # 空則 fallback lcc 代碼
            if domain_name:
                system_prompt = system_prompt + (
                    f"\n\n本文件主題領域：{domain_name}，請以該領域標準術語翻譯。"
                )

        # ④ Glossary 術語強約束區塊（gated 旗標；含大小寫不敏感指令）
        if settings.LLM_USE_GLOSSARY_ALIGN and ctx.glossary:
            term_lines = "\n".join(
                f"- {term_key} → {translation}"
                for term_key, translation in ctx.glossary.items()
            )
            system_prompt = system_prompt + (
                "\n\n【術語強約束 System constraint】以下專有名詞譯法不可違背，翻譯時必須與論文譯本完全一致"
                "（大小寫不敏感：正文出現相同單詞時，無論其原文大小寫，均強制套用該對應譯法）：\n"
                f"{term_lines}"
            )

        # ⑤ 額外約束注入（ctx.constraints；文字級約束，不 gate 旗標）
        if ctx.constraints:
            rule_lines = "\n".join(f"- {item}" for item in ctx.constraints)
            system_prompt = system_prompt + f"\n\n【額外譯文約束】：\n{rule_lines}"

        return system_prompt

    # ------------------------------------------------------------------ #
    # 用戶提示詞拼接（plan U2）
    # ------------------------------------------------------------------ #
    def _build_user_prompt(self, text: str, ctx: "InjectionContext", text_type: str = "content") -> str:
        if text_type == "title":
            return f"需要翻译的标题:\n{text}\n\n直接输出："
        if text_type == "abstract":
            return f"需要翻译的内容:\n{text}\n\n直接输出："
        if ctx.zh_summary:
            return f"摘要翻译参考:\n{ctx.zh_summary}\n\n需要翻译的内容:\n{text}\n\n直接输出："
        if ctx.preceding:
            return f"前文翻译参考:\n{ctx.preceding}\n\n需要翻译的内容:\n{text}\n\n直接输出："
        return f"需要翻译的内容:\n{text}\n\n直接输出："
# === [TRANSLATOR C2 END] ===

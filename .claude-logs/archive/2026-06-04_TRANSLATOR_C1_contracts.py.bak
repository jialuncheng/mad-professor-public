"""PIPE-CORE 四份凍結 Phase 交接合約（對齊 PIPE-SPEC §1.1）。

三層解耦的「狀態層合約」：每份子模型是一個 Phase 的產出契約，凍結（frozen）以
保證跨 Phase 傳遞時不可變、型別安全，取代舊 `pipeline_core.py` 的可變 dict 黑盒。

凍結語意（Pydantic v2）：`model_config = ConfigDict(frozen=True)` → 實例不可變。
R1.1 邊界（交接點①）：`IngestionMetadataSpec` 以 `extra='forbid'` 在 schema 層
拒絕 Abstract / LCC / Glossary 等欄位混入（P1 越界即 ValidationError）。

本檔為 PIPE-CORE OP-1 交付物，**不含任何 doc_type 業務細節、不接線既有 processor**。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class IngestionMetadataSpec(BaseModel):
    """合約① P1 → P2：純解析 + 原文元數據（PIPE-SPEC §1.1 ①）。

    根節點含三軸融合 Resolved 完畢的**原文** Title / Author / 出處 / DOI；
    JSON 樹章節 Tiles 已按 Section/Chapter 物理分組。
    🚫 不含 Abstract / LCC / Glossary、零翻譯（`extra='forbid'` 於 schema 層保證 R1.1）。
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    title: str
    authors: List[str] = []
    venue: Optional[str] = None
    doi: Optional[str] = None
    source_lang: str  # 文件原生語言（原文）
    tiles: List[Dict[str, Any]] = []  # 已按 Section/Chapter 物理分組的章節 Tiles


class GlossaryReadySpec(BaseModel):
    """合約② P2 → P3：摘要 + LCC + 凍結 Glossary + translated_abstract（PIPE-SPEC §1.1 ②）。

    原文摘要 + 標準 LCC 分類碼 + 凍結最終 Glossary（doc/book ⊕ sqlite 融合去重）
    + translated_abstract（目標語、一次到位）；Book 各章 chapter_summary 亦於此交付。
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    abstract: str  # 原文摘要
    lcc: str  # 標準 LCC 一級分類碼（由 DomainNormalizer 收斂）
    glossary: Dict[str, str]  # 凍結最終 Glossary（融合去重後）
    translated_abstract: str  # 目標語摘要（一次到位、R2.2）
    chapter_summaries: Optional[List[str]] = None  # Book 滾動章節摘要（非 Book 為 None）


class BilingualMarkdownSpec(BaseModel):
    """合約③ P3 → P4：100% 乾淨雙語 Markdown（PIPE-SPEC §1.1 ③）。

    硬碟雙語 Markdown final_zh.md / final_en.md 與對應 JSON 節點；
    translated_abstract 由 P2 寫入並沿用。🚫 嚴禁含 AI Questions / Summary / 公式雜訊。
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    final_zh_path: str
    final_en_path: str
    translated_abstract: str  # 由 P2 沿用
    rag_tree_json: Optional[Dict[str, Any]] = None  # 對應 JSON 節點（可選）


class RagDbSpec(BaseModel):
    """合約④ P4 → 外部：RAG/DB 落地（PIPE-SPEC §1.1 ④）。

    SQLite Paper + PaperChunk 表結構 + vectors/ 物理目錄 + index_meta.json。
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    vectors_path: str
    paper_chunk_count: int = 0
    index_meta: Dict[str, Any] = {}

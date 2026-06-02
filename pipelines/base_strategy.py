"""PIPE-CORE DocumentStrategy 抽象基類與 NullStrategy 哨兵（plan v2 U3）。

三層解耦的「策略層介面」：定義五路統一的四 Phase 方法簽名，供 PIPE-RESUME/VISUAL/
ACADEMIC/LITEDOC/BOOK 各 plan 實作。**骨架階段不附任何具體五路實作**。

`NullStrategy`：未註冊任何策略時的顯式失敗哨兵——四 Phase 一律拋 `NotImplementedError`，
防止「無策略時靜默跑空通過」。Flip 後五路齊全仍保留作防呆。

本檔為 PIPE-CORE OP-2 交付物，**不含任何 doc_type 業務細節、不接線既有 processor**。
"""

from __future__ import annotations

import abc

from pipelines.context import PipelineContext
from pipelines.contracts import (
    BilingualMarkdownSpec,
    GlossaryReadySpec,
    IngestionMetadataSpec,
    RagDbSpec,
)


class DocumentStrategy(abc.ABC):
    """五路策略統一介面（四 Phase 方法 + RAG 字數門檻）。

    `rag_char_threshold`：RAG 入庫的最小有效字數門檻——一般文檔 ≥10、Vision 短文檔
    （slides/resume）≥3（SPEC §3.1）；由各路具體策略覆寫。
    """

    rag_char_threshold: int = 10

    @abc.abstractmethod
    def run_phase1(self, ctx: PipelineContext) -> IngestionMetadataSpec:
        """P1 Ingestion：純解析 + 原文元數據（合約①）。"""

    @abc.abstractmethod
    def run_phase2(self, ctx: PipelineContext) -> GlossaryReadySpec:
        """P2 Glossary & Context Prep：摘要 + LCC + 凍結 Glossary（合約②）。"""

    @abc.abstractmethod
    def run_phase3(self, ctx: PipelineContext) -> BilingualMarkdownSpec:
        """P3 Translation & Restore：乾淨雙語 Markdown（合約③）。"""

    @abc.abstractmethod
    def run_phase4(self, ctx: PipelineContext) -> RagDbSpec:
        """P4 Async RAG：向量化落庫（合約④，非阻塞）。"""


class NullStrategy(DocumentStrategy):
    """空策略哨兵：未註冊任何具體策略時回傳之，四 Phase 拋 NotImplementedError。"""

    rag_char_threshold: int = 10

    _MSG = "骨架階段無具體策略（NullStrategy）；具體五路實作屬 PIPE-RESUME/VISUAL/ACADEMIC/LITEDOC/BOOK plan"

    def run_phase1(self, ctx: PipelineContext) -> IngestionMetadataSpec:
        raise NotImplementedError(self._MSG)

    def run_phase2(self, ctx: PipelineContext) -> GlossaryReadySpec:
        raise NotImplementedError(self._MSG)

    def run_phase3(self, ctx: PipelineContext) -> BilingualMarkdownSpec:
        raise NotImplementedError(self._MSG)

    def run_phase4(self, ctx: PipelineContext) -> RagDbSpec:
        raise NotImplementedError(self._MSG)

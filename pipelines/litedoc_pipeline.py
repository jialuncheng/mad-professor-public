# === [PIPE-LITEDOC C2] ===
"""LiteDocPipeline 策略管線（PIPE 縱向五路第 3 路：news / web / unknown）。

`@PipelineFactory.register('litedoc'/'news'/'web')` 三 key 註冊；unknown doc_type 經 factory
`_FALLBACK_DOC_TYPE='litedoc'` 自動承接（SPEC §3.3 最後防線）。主幹（Orchestrator）零 doc_type 分支。

本路為 academic-lite：P1 MinerU+md_cleaner 文字攝入（非 Vision）、P2-P4 全消費已落地共用真理源
（`section_engine` / DomainNormalizer / GlossaryManager / Translator / rag_indexer），不重造機制。

C2 範圍：骨架與三 key 註冊——四 Phase 為 strict stub（拋 NotImplementedError）；
P1-P4 具體實作屬後續 C3-C6（plan U2-U6）。
"""

from __future__ import annotations

import logging

from pipelines.base_strategy import DocumentStrategy
from pipelines.context import PipelineContext
from pipelines.contracts import (
    BilingualMarkdownSpec,
    GlossaryReadySpec,
    IngestionMetadataSpec,
    RagDbSpec,
)
from pipelines.factory import PipelineFactory

logger = logging.getLogger(__name__)


@PipelineFactory.register("litedoc")
@PipelineFactory.register("news")
@PipelineFactory.register("web")
class LiteDocPipeline(DocumentStrategy):
    """第 3 路策略：news / web / unknown（fallback）。

    `rag_char_threshold=10`：litedoc 為長篇散文型、非 Vision 短文（slides/resume ≥3），
    走一般文檔門檻 ≥10（對齊 master plan v10 L183、rag_indexer `is_chunk_meaningful` 預設）。
    """

    rag_char_threshold: int = 10

    _STUB_MSG = (
        "LiteDocPipeline C2 骨架階段——四 Phase 具體實作屬 PIPE-LITEDOC C3-C6"
        "（P1 MinerU 攝入 / P2 六步 / P3 size-gate 翻譯 / P4 Async RAG）"
    )

    def run_phase1(self, ctx: PipelineContext) -> IngestionMetadataSpec:
        """P1 Ingestion（C3 實作）。"""
        raise NotImplementedError(self._STUB_MSG)

    def run_phase2(self, ctx: PipelineContext) -> GlossaryReadySpec:
        """P2 Glossary & Context Prep（C4 實作）。"""
        raise NotImplementedError(self._STUB_MSG)

    def run_phase3(self, ctx: PipelineContext) -> BilingualMarkdownSpec:
        """P3 Translation & Restore（C5 實作）。"""
        raise NotImplementedError(self._STUB_MSG)

    def run_phase4(self, ctx: PipelineContext) -> RagDbSpec:
        """P4 Async RAG（C6 實作）。"""
        raise NotImplementedError(self._STUB_MSG)
# === [PIPE-LITEDOC C2 END] ===

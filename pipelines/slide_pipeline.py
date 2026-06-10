"""SlidePipeline —— 簡報（slides）策略管線（PIPE 縱向五路絞殺第 2 路、PIPE-SLIDES）。

`@PipelineFactory.register('slides')` 註冊；主幹（Orchestrator）零 doc_type 分支、
僅透過 DocumentStrategy 四方法合約呼叫本策略。

四 Phase 規格（PIPE-SLIDES plan v1〔v1.1〕U1-U11；後續 commit 逐步落地）：
- P1 Ingestion（C2）：每頁整頁存圖（fitz get_pixmap、自建不耦合 A 軌 slides_processor）
  + Vision 忠實轉錄（SPEC §1.3.1：LLM_VISION_TEMPERATURE=0）+ 條件式滾動（預設關）
  + 封面判定（title fallback 檔名、簡報欄走 ctx.raw_metadata 旁路）+ 跨頁統計去重（排除封面）。
- P2 Glossary & Context Prep（C3）：統一六步（section=頁；① 順產 raw_domain、
  ② 順產缺失頁標題；key＝p{頁序}_{原文頁標題}——三方同基準、根除重複標題覆蓋）。
- P3 Translation & Restore（C4）：逐頁並行翻譯（RESUME-PERF-1 範式）+ 圖片 alt 對齊
  （雙 Caption 物理根除、MD-RESTORE slides 部分）+ ctx.rag_sections 旁路 + zh 來源 path
  + 退化 fallback；不渲染 meta header。
- P4 Async RAG（C5）：rag_indexer 共用真理源（四產物、零 A 軌依賴）。

C1（本檔現階段）僅交付：註冊 + 四方法合約 stub + rag_char_threshold=3（U11、
保 'SiC'/'THD' 級短關鍵詞）。strict 合約：未落地 Phase 拋 NotImplementedError、
由 Orchestrator 對齊 NullStrategy 行為攔截（影子 B 軌、線上 0 風險）。
"""
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


@PipelineFactory.register('slides')
class SlidePipeline(DocumentStrategy):
    """簡報策略：Vision 每頁解析、逐頁翻譯、頁級 RAG。"""

    # U11：Vision 短文檔門檻放寬（保 'SiC'/'THD'/'LLC' 級短技術詞；資料庫 SOP ≥3 先例同 resume）
    rag_char_threshold: int = 3

    def run_phase1(self, ctx: PipelineContext) -> IngestionMetadataSpec:
        """P1 Ingestion：每頁存圖 + Vision 轉錄 + 封面判定 + 統計去重（C2 落地）。"""
        raise NotImplementedError("SlidePipeline.run_phase1 於 PIPE-SLIDES C2 落地")

    def run_phase2(self, ctx: PipelineContext) -> GlossaryReadySpec:
        """P2 統一六步（section=頁、key=p{N}_{原文頁標題}）（C3 落地）。"""
        raise NotImplementedError("SlidePipeline.run_phase2 於 PIPE-SLIDES C3 落地")

    def run_phase3(self, ctx: PipelineContext) -> BilingualMarkdownSpec:
        """P3 逐頁翻譯 + alt 對齊還原 + rag_sections 旁路（C4 落地）。"""
        raise NotImplementedError("SlidePipeline.run_phase3 於 PIPE-SLIDES C4 落地")

    def run_phase4(self, ctx: PipelineContext) -> RagDbSpec:
        """P4 rag_indexer 共用真理源接線（C5 落地）。"""
        raise NotImplementedError("SlidePipeline.run_phase4 於 PIPE-SLIDES C5 落地")

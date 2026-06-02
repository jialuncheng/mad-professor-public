"""PIPE-CORE Orchestrator 指揮層（plan v2 U1 / U4 / §2.5.1）。

三層解耦的「指揮層」：唯一職責＝保證每 Phase 按四 Phase DAG 順序、依 Context 合約
正確交付。以**宣告式 Phase 序列**（`_PHASES`）推進 P1→P2→P3→P4，**零 doc_type
字面量分支**（所有 doc_type 專屬 how 下放策略插件，經 PipelineFactory 取得）。

交接點驗證（U4）：每 Phase 產出強制以合約型別斷言；P1–P3 驗證失敗 → 拋
`OrchestratorError` 中止（FAILED 語意）；P4 失敗 → 僅標 `rag_status='failed'` +
warning，不阻主鏈、不影響 `reading_ready`（SPEC R4.2）。

掛點（骨架定義介面、實作可注入）：Early Emit（P1 後）、Checkpoint（每 Phase 邊界）、
P4 非阻塞派發（injectable dispatcher；真正 BackgroundTasks 屬 RAG-ASYNC plan）。

本檔為 PIPE-CORE OP-3 交付物，**不含任何具體五路策略實作、不接線既有 processor**。
"""

from __future__ import annotations

import logging
from typing import Callable, List, Optional, Tuple, Type

from pipelines.context import PhaseEnum, PipelineContext
from pipelines.contracts import (
    BilingualMarkdownSpec,
    GlossaryReadySpec,
    IngestionMetadataSpec,
    RagDbSpec,
)
from pipelines.factory import PipelineFactory

logger = logging.getLogger(__name__)


class OrchestratorError(Exception):
    """P1–P3 交接點驗證失敗（FAILED 語意、中止後續 Phase）。"""

    def __init__(self, phase: PhaseEnum, reason: str):
        self.phase = phase
        self.reason = reason
        super().__init__(f"[{phase.value}] {reason}")


# 宣告式同步推進三 Phase 規格：(phase, 策略方法名, ctx 寫入欄位, 預期合約型別)
# 注意：純資料宣告、零 doc_type 字面量分支（三層解耦自證）。
_PHASES: List[Tuple[PhaseEnum, str, str, Type]] = [
    (PhaseEnum.P1, "run_phase1", "ingestion", IngestionMetadataSpec),
    (PhaseEnum.P2, "run_phase2", "glossary_ready", GlossaryReadySpec),
    (PhaseEnum.P3, "run_phase3", "bilingual", BilingualMarkdownSpec),
]


class Orchestrator:
    """四 Phase DAG 指揮層（零業務細節）。"""

    def __init__(
        self,
        early_emit_hook: Optional[Callable[[PipelineContext], None]] = None,
        checkpoint_hook: Optional[Callable[[PipelineContext], None]] = None,
        dispatch_p4: Optional[Callable[["object", PipelineContext], None]] = None,
    ):
        self.early_emit_hook = early_emit_hook
        self.checkpoint_hook = checkpoint_hook
        # 注入式 P4 派發器（骨架預設同步樁；真正非阻塞 BackgroundTasks 屬 RAG-ASYNC plan）
        self._dispatch_p4 = dispatch_p4 or self._default_dispatch_p4

    def run(self, ctx: PipelineContext) -> PipelineContext:
        """推進四 Phase DAG（plan v2 §2.5.1）。"""
        # 1. 取策略（未命中降級 LiteDoc / 無策略回 NullStrategy）——零 doc_type 分支
        strategy = PipelineFactory.get_strategy(ctx.doc_type)

        # 影子命名貫穿（SPEC §3.5）：shadow=True → paper_id 尾綴 _shadow
        if ctx.shadow and not ctx.paper_id.endswith("_shadow"):
            ctx.paper_id = f"{ctx.paper_id}_shadow"

        logger.info(
            f"[orchestrator] run paper={ctx.paper_id} doc_type={ctx.doc_type} "
            f"shadow={ctx.shadow} strategy={type(strategy).__name__}"
        )

        # 2. 宣告式推進 P1→P3（同步、交接點驗證）
        for phase, runner_name, field, expected in _PHASES:
            ctx.phase = phase
            result = getattr(strategy, runner_name)(ctx)
            # 交接點驗證（U4）：合約型別斷言（① R1.1 禁欄位由合約 extra='forbid' 結構保證）
            if not isinstance(result, expected):
                raise OrchestratorError(
                    phase,
                    f"交接點驗證失敗：預期 {expected.__name__}、得 {type(result).__name__}",
                )
            setattr(ctx, field, result)
            if self.checkpoint_hook:
                self.checkpoint_hook(ctx)  # Checkpoint 邊界掛點
            if phase is PhaseEnum.P1 and self.early_emit_hook:
                self.early_emit_hook(ctx)  # Early Emit（Title/Author 快軌）
            if phase is PhaseEnum.P3:
                ctx.reading_ready = True  # 閱讀器/Print PDF 解鎖（SPEC R4.1）

        # 3. P4 非阻塞派發（不在主鏈 await；失敗僅標記、不阻主鏈，SPEC R4.2）
        ctx.phase = PhaseEnum.P4
        self._dispatch_p4(strategy, ctx)
        return ctx

    @staticmethod
    def _default_dispatch_p4(strategy, ctx: PipelineContext) -> None:
        """骨架預設 P4 派發樁（同步執行 + 容錯）。真正背景任務由 RAG-ASYNC plan 注入。"""
        try:
            result = strategy.run_phase4(ctx)
            if not isinstance(result, RagDbSpec):
                raise TypeError(
                    f"P4 預期 RagDbSpec、得 {type(result).__name__}"
                )
            ctx.rag = result
            ctx.rag_status = "ready"  # 解鎖 AI Chat
        except Exception as e:
            # R4.2：RAG 失敗僅 warning + 標 rag_failed，不阻主鏈、不影響 reading_ready
            logger.warning(
                f"[orchestrator] P4 RAG 失敗（不阻主鏈、標 rag_status=failed）: {e}",
                exc_info=True,
            )
            ctx.rag_status = "failed"

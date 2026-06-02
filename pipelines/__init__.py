"""PIPE-CORE 三層解耦調度套件（PIPE 大改版新核心，與舊 pipeline_core.py 物理共存）。

OP-1 交付：合約層（contracts）+ 狀態層（context）。
OP-2/OP-3 將補：策略層（base_strategy / factory）+ 指揮層（orchestrator）。
"""

from pipelines.context import PhaseEnum, PipelineContext
from pipelines.contracts import (
    BilingualMarkdownSpec,
    GlossaryReadySpec,
    IngestionMetadataSpec,
    RagDbSpec,
)

__all__ = [
    "PhaseEnum",
    "PipelineContext",
    "IngestionMetadataSpec",
    "GlossaryReadySpec",
    "BilingualMarkdownSpec",
    "RagDbSpec",
]

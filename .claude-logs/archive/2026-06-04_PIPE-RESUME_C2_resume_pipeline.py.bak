"""PIPE-RESUME ResumePipeline 策略管線（plan_v1、PIPE 縱向五路絞殺第 1 路）。

Resume（履歷）文體的四 Phase 策略插件，繼承 PIPE-CORE `DocumentStrategy`，以
`@PipelineFactory.register('resume')` 註冊；主幹（Orchestrator）零 doc_type 分支、
僅以 `PipelineFactory.get_strategy('resume')` 取得本策略。

四 Phase 對映落地 ABC 抽象方法：
- run_phase1 → IngestionMetadataSpec（P1 Vision 整份解析 + 原文元數據）
- run_phase2 → GlossaryReadySpec（P2 LCC 分類 / 摘要 / Glossary 自癒 / 摘要翻譯）
- run_phase3 → BilingualMarkdownSpec（P3 100% Bypass 翻譯與還原）
- run_phase4 → RagDbSpec（P4 非同步 RAG、門檻 ≥3 技能詞保護）

本檔為 C1（策略骨架與工廠註冊）交付：僅註冊插件 + 四方法 stub；
具體 Phase 實作屬 C2（P1）/ C3（P2）/ C4（P3）/ C5（P4）。

> custom_metadata 硬前置（tasks §9）：P1 履歷專屬欄 phone/email/domain 於凍結合約
> `IngestionMetadataSpec`（extra="forbid"）尚未具備落點前，暫存於本策略實例
> `self._raw_meta` 穿線給 P2；正式接線待上游擴 custom_metadata 後另行授權。
"""

# === [PIPE-RESUME C1 START] ===
from __future__ import annotations

import logging
from typing import Any, Dict

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

# C2-C5 各 Phase 實作前的統一佔位訊息（明示尚未落地之 Phase）。
_NOT_IMPLEMENTED_MSG = (
    "ResumePipeline.{phase} 尚未實作（PIPE-RESUME {commit}）；"
    "本 Commit（C1）僅交付策略骨架與工廠註冊。"
)


@PipelineFactory.register("resume")
class ResumePipeline(DocumentStrategy):
    """Resume 文體四 Phase 策略（C1 骨架；Phase 實作待 C2-C5）。"""

    # SPEC §3.1：Vision 短文檔（resume/slides）RAG 入庫字數門檻放寬至 3（保 Python/Docker 等技能詞）。
    rag_char_threshold: int = 3

    def __init__(self) -> None:
        # interim 穿線容器（tasks §9 硬前置）：P1 抽出的 phone/email/domain 暫存於此，
        # 供 P2 消費 domain 餵 normalize_to_lcc；待 custom_metadata 正式入合約後改走合約欄。
        self._raw_meta: Dict[str, Any] = {}

    def run_phase1(self, ctx: PipelineContext) -> IngestionMetadataSpec:
        """P1 Ingestion：純解析 + 原文元數據（合約①）。實作見 C2。"""
        raise NotImplementedError(
            _NOT_IMPLEMENTED_MSG.format(phase="run_phase1", commit="C2")
        )

    def run_phase2(self, ctx: PipelineContext) -> GlossaryReadySpec:
        """P2 Glossary & Context Prep：LCC / 摘要 / Glossary 自癒 / 摘要翻譯（合約②）。實作見 C3。"""
        raise NotImplementedError(
            _NOT_IMPLEMENTED_MSG.format(phase="run_phase2", commit="C3")
        )

    def run_phase3(self, ctx: PipelineContext) -> BilingualMarkdownSpec:
        """P3 Translation & Restore：100% Bypass 乾淨雙語 Markdown（合約③）。實作見 C4。"""
        raise NotImplementedError(
            _NOT_IMPLEMENTED_MSG.format(phase="run_phase3", commit="C4")
        )

    def run_phase4(self, ctx: PipelineContext) -> RagDbSpec:
        """P4 Async RAG：向量化落庫、門檻 ≥3（合約④，非阻塞）。實作見 C5。"""
        raise NotImplementedError(
            _NOT_IMPLEMENTED_MSG.format(phase="run_phase4", commit="C5")
        )
# === [PIPE-RESUME C1 END] ===

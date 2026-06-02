"""PIPE-CORE 契約測試（plan v2 §6.1）。

OP-1：合約與狀態層——四份凍結合約 frozen 斷言、交接點① R1.1 禁欄位攔截、
必填欄位驗證、PipelineContext 預設與 Phase 推進。
（OP-2 工廠/策略、OP-3 Orchestrator DAG 測試於後續 OP 追加至本檔。）
"""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipelines.context import PhaseEnum, PipelineContext  # noqa: E402
from pipelines.contracts import (  # noqa: E402
    BilingualMarkdownSpec,
    GlossaryReadySpec,
    IngestionMetadataSpec,
    RagDbSpec,
)


# ── 交接點① R1.1：IngestionMetadataSpec 禁含 Abstract/LCC/Glossary ──

def test_ingestion_valid_construct():
    spec = IngestionMetadataSpec(title="T", source_lang="en", authors=["A"])
    assert spec.title == "T"
    assert spec.tiles == []


def test_ingestion_rejects_abstract_lcc_glossary():
    # extra='forbid' → 任一禁欄位混入即 ValidationError（P1 越界攔截）
    for forbidden in ({"abstract": "x"}, {"lcc": "BF"}, {"glossary": {}}):
        with pytest.raises(ValidationError):
            IngestionMetadataSpec(title="T", source_lang="en", **forbidden)


# ── 交接點② 必填欄位 ──

def test_glossary_ready_requires_translated_abstract():
    with pytest.raises(ValidationError):
        GlossaryReadySpec(abstract="a", lcc="BF", glossary={})  # 缺 translated_abstract


def test_glossary_ready_valid():
    spec = GlossaryReadySpec(
        abstract="原文摘要", lcc="BF", glossary={"k": "v"},
        translated_abstract="譯文摘要",
    )
    assert spec.translated_abstract == "譯文摘要"
    assert spec.chapter_summaries is None


# ── 合約凍結（frozen）斷言 ──

def test_contracts_are_frozen():
    ing = IngestionMetadataSpec(title="T", source_lang="en")
    with pytest.raises(ValidationError):
        ing.title = "changed"  # frozen → 不可變
    bil = BilingualMarkdownSpec(
        final_zh_path="a_zh.md", final_en_path="a_en.md", translated_abstract="x"
    )
    with pytest.raises(ValidationError):
        bil.final_zh_path = "y"
    rag = RagDbSpec(vectors_path="vectors/")
    with pytest.raises(ValidationError):
        rag.vectors_path = "z"


# ── PipelineContext 狀態載體 ──

def test_context_defaults():
    ctx = PipelineContext(doc_type="academic", paper_id="p1")
    assert ctx.phase is PhaseEnum.P1
    assert ctx.reading_ready is False
    assert ctx.rag_status == "pending"
    assert ctx.shadow is False
    # 四合約欄位寫入前為 None
    assert ctx.ingestion is None
    assert ctx.glossary_ready is None
    assert ctx.bilingual is None
    assert ctx.rag is None


def test_context_carries_frozen_contract_and_phase_advances():
    ctx = PipelineContext(doc_type="resume", paper_id="p2", shadow=True)
    ctx.ingestion = IngestionMetadataSpec(title="T", source_lang="en")
    ctx.phase = PhaseEnum.P2
    assert ctx.shadow is True
    assert ctx.ingestion.title == "T"
    assert ctx.phase is PhaseEnum.P2
    # 承載的合約子模型仍凍結
    with pytest.raises(ValidationError):
        ctx.ingestion.title = "x"


def test_rag_status_rejects_invalid_literal():
    with pytest.raises(ValidationError):
        PipelineContext(doc_type="academic", paper_id="p", rag_status="bogus")

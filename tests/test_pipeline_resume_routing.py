"""Phase 4.7e Commit 7e-2：pipeline resume routing 測試。

驗證 doc_type='resume' 時：
1. _stage_pdf_to_md 走 ResumeProcessor、不走 self.pdf_processor (MinerU)
2. _stage_pdf_to_md 跳過 self.md_cleaner.clean()
3. DocAnalyzer._fix_heading_levels 不打 LLM、直接 return
4. DocAnalyzer._analyze_document_structure 寫最小 sidecar、不打 LLM

對照 doc_type='academic' 走既有 MinerU + LLM 路徑、確認路由正確切分。
"""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline_core import PipelineCore  # noqa: E402
from processor.doc_analyzer import DocAnalyzer  # noqa: E402


# ─────────────────── helper ───────────────────
def _make_pipeline(tmp_path):
    """建 PipelineCore 並注入 mock processors（繞 lazy property）。"""
    pc = PipelineCore()
    pc.paper_info = {'paper_id': 'test', 'output_dir': str(tmp_path)}
    # 直接設 _xxx underscore 屬性、跳 property lazy init
    pc._pdf_processor = MagicMock()
    pc._md_cleaner = MagicMock()
    # parser.parse() 都要回真實 Path（後續 md_cleaner.clean(markdown_path) 需要）
    fake_md = tmp_path / "fake.md"
    fake_md.write_text("# fake", encoding='utf-8')
    pc._pdf_processor.parse.return_value = fake_md
    return pc, fake_md


# ─────────────────── pipeline routing tests ───────────────────
def test_pdf_to_md_routes_resume_to_resume_processor(tmp_path):
    """doc_type='resume' → 走 ResumeProcessor.parse、不走 MinerU。"""
    pc, fake_md = _make_pipeline(tmp_path)
    with patch('pipeline_core.ResumeProcessor') as MockRP:
        instance = MockRP.return_value
        instance.parse.return_value = fake_md
        result = pc._stage_pdf_to_md(
            'fake.pdf', tmp_path, 'fake',
            {'_confirmed_doc_type': 'resume'}
        )
    MockRP.assert_called_once()
    instance.parse.assert_called_once()
    pc._pdf_processor.parse.assert_not_called()
    assert result == fake_md


def test_pdf_to_md_routes_academic_to_mineru(tmp_path):
    """doc_type='academic' → 走 self.pdf_processor (MinerU)、不創 ResumeProcessor。"""
    pc, fake_md = _make_pipeline(tmp_path)
    with patch('pipeline_core.ResumeProcessor') as MockRP, \
         patch('pipeline_core.SlidesProcessor') as MockSP:
        pc._stage_pdf_to_md(
            'fake.pdf', tmp_path, 'fake',
            {'_confirmed_doc_type': 'academic'}
        )
    pc._pdf_processor.parse.assert_called_once()
    MockRP.assert_not_called()
    MockSP.assert_not_called()


def test_pdf_to_md_skips_md_cleaner_for_resume(tmp_path):
    """doc_type='resume' → 不呼叫 md_cleaner.clean()。"""
    pc, fake_md = _make_pipeline(tmp_path)
    with patch('pipeline_core.ResumeProcessor') as MockRP:
        MockRP.return_value.parse.return_value = fake_md
        pc._stage_pdf_to_md(
            'fake.pdf', tmp_path, 'fake',
            {'_confirmed_doc_type': 'resume'}
        )
    pc._md_cleaner.clean.assert_not_called()


def test_pdf_to_md_runs_md_cleaner_for_academic(tmp_path):
    """doc_type='academic' → md_cleaner.clean() 必呼叫（對照）。"""
    pc, fake_md = _make_pipeline(tmp_path)
    pc._stage_pdf_to_md(
        'fake.pdf', tmp_path, 'fake',
        {'_confirmed_doc_type': 'academic'}
    )
    pc._md_cleaner.clean.assert_called_once_with(fake_md)


def test_pdf_to_md_unknown_doctype_logs_warning_and_falls_back(tmp_path, caplog):
    """未知 doc_type → fallback MinerU + log warning。"""
    import logging
    pc, _ = _make_pipeline(tmp_path)
    with caplog.at_level(logging.WARNING):
        pc._stage_pdf_to_md(
            'fake.pdf', tmp_path, 'fake',
            {'_confirmed_doc_type': 'mystery_type'}
        )
    pc._pdf_processor.parse.assert_called_once()
    assert any("未知 doc_type='mystery_type'" in r.message for r in caplog.records)


# ─────────────────── doc_analyzer short-circuit tests ───────────────────
def test_doc_analyzer_skips_resume_heading_fix(tmp_path):
    """doc_type='resume' → _fix_heading_levels 不打 LLM、直接 return。"""
    md = tmp_path / "resume.md"
    md.write_text(
        "# CTO Resume - Test\n## Working Experience\n### ACME - CTO (2020 - PRESENT)\n",
        encoding='utf-8'
    )
    mock_llm = MagicMock()
    analyzer = DocAnalyzer(llm=mock_llm)
    analyzer._fix_heading_levels(md, 'resume')
    mock_llm.chat.assert_not_called()
    mock_llm.chat_with_image.assert_not_called()


def test_doc_analyzer_calls_llm_for_academic_heading_fix(tmp_path):
    """doc_type='academic' → 對照組：LLM 必被呼叫（fix_heading_levels 路徑）。"""
    md = tmp_path / "paper.md"
    md.write_text("# Title\n## Abstract\n## Introduction\n", encoding='utf-8')
    mock_llm = MagicMock()
    # fix_heading_levels util 內部使用 llm.chat；mock 回不影響的合法字串
    mock_llm.chat.return_value = '{}'
    analyzer = DocAnalyzer(llm=mock_llm)
    analyzer._fix_heading_levels(md, 'academic')
    # academic 路徑會呼叫 LLM；確認 mock 有被觸發（不嚴格驗 args）
    assert mock_llm.chat.called or mock_llm.chat_with_image.called


def test_doc_analyzer_writes_minimal_sidecar_for_resume(tmp_path):
    """doc_type='resume' → _analyze_document_structure 寫最小 sidecar、不打 LLM。"""
    md = tmp_path / "resume.md"
    md.write_text("# CTO Resume - Test\n## Working Experience\n", encoding='utf-8')
    mock_llm = MagicMock()
    analyzer = DocAnalyzer(llm=mock_llm)
    result = analyzer._analyze_document_structure(md, 'resume')

    # 不打 LLM
    mock_llm.chat.assert_not_called()
    # sidecar 落地
    sidecar = tmp_path / "resume_doc_structure.json"
    assert sidecar.exists()
    payload = json.loads(sidecar.read_text(encoding='utf-8'))
    assert payload == {
        "structure": [],
        "document_type": "resume",
        "flat_structure": True,
    }
    # return value 對齊
    assert result == payload

"""Phase 4.7e Commit 7e-2 v2：pipeline resume routing 測試。

驗證 doc_type='resume' 時 _stage_pdf_to_md：
1. 走 ResumeProcessor、不走 self.pdf_processor (MinerU)
2. 跳過 self.md_cleaner.clean()

對照組：
- doc_type='academic' → MinerU + md_cleaner（既有路徑不破）
- doc_type='slides' → SlidesProcessor + 跳過 md_cleaner（既有路徑不破）
- 未知 doc_type → fallback MinerU + log warning

⚠ 本 commit baron Q6 決策：**doc_analyzer 不短路**，故無 doc_analyzer
相關測試（academic heading_fix LLM 對 resume 也跑、做為 ResumeProcessor
偶爾誤判 # 數量時的雙保險）。
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline_core import PipelineCore  # noqa: E402


def _make_pipeline(tmp_path):
    """建 PipelineCore 並注入 mock processors（繞 lazy property）。"""
    pc = PipelineCore()
    pc.paper_info = {'paper_id': 'test', 'output_dir': str(tmp_path)}
    # 直接設 _xxx underscore 屬性、跳 property lazy init
    pc._pdf_processor = MagicMock()
    pc._md_cleaner = MagicMock()
    fake_md = tmp_path / "fake.md"
    fake_md.write_text("# fake", encoding='utf-8')
    pc._pdf_processor.parse.return_value = fake_md
    return pc, fake_md


def test_pdf_to_md_routes_resume_to_resume_processor(tmp_path):
    """doc_type='resume' → 呼叫 ResumeProcessor.parse、不呼叫 MinerU。"""
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
    """doc_type='academic' → 走 self.pdf_processor、不創 ResumeProcessor/SlidesProcessor。"""
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


def test_pdf_to_md_slides_routing_still_works(tmp_path):
    """doc_type='slides' → 仍走 SlidesProcessor + 跳過 md_cleaner（既有路徑不破）。"""
    pc, fake_md = _make_pipeline(tmp_path)
    with patch('pipeline_core.SlidesProcessor') as MockSP, \
         patch('pipeline_core.ResumeProcessor') as MockRP:
        MockSP.return_value.parse.return_value = fake_md
        pc._stage_pdf_to_md(
            'fake.pdf', tmp_path, 'fake',
            {'_confirmed_doc_type': 'slides'}
        )
    MockSP.assert_called_once()
    MockSP.return_value.parse.assert_called_once()
    MockRP.assert_not_called()
    pc._pdf_processor.parse.assert_not_called()
    pc._md_cleaner.clean.assert_not_called()

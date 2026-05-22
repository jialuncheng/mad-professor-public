"""Phase 4.7? MODEL-1+2 階段 B2: rag_processor._is_chunk_meaningful 驗證。

驗證：
- 空字串 / 純數字 / 過短 chunk 過濾
- 修正 2: markdown 噪聲（#/*/_/~/`/-/+/>/|/[/]/空白）移除後再計算
- 修正 4: doc_type 'resume'/'slides' 放寬到 3 字元
- 修正 4: email / phone / url 保留（不論長度）
- baron 補充二: Python / Docker 等技能詞在 resume 不被誤殺

依據:
- plan §4.2 + §3.6.2 修正 2 + §3.6.4 修正 4
- plan §6.1 修正版
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _make_doc(text, metadata=None):
    """建構符合 LangChain Document 介面的 mock 物件。"""
    class Doc:
        def __init__(self, t, m):
            self.page_content = t
            self.metadata = m or {}
    return Doc(text, metadata)


# ─────────────────── 基本規則（4 個）───────────────────


def test_filter_empty_string():
    """空字串 / 純空白 過濾。"""
    from processor.rag_processor import _is_chunk_meaningful
    assert not _is_chunk_meaningful(_make_doc(""), doc_type="academic")
    assert not _is_chunk_meaningful(_make_doc("   "), doc_type="academic")


def test_filter_pure_digits():
    """純年份 / 純頁碼 過濾、不論 doc_type。"""
    from processor.rag_processor import _is_chunk_meaningful
    assert not _is_chunk_meaningful(_make_doc("2024"), doc_type="academic")
    assert not _is_chunk_meaningful(_make_doc("2024"), doc_type="resume")
    assert not _is_chunk_meaningful(_make_doc("123"), doc_type="slides")


def test_keep_long_text():
    """≥ 10 字元正常保留。"""
    from processor.rag_processor import _is_chunk_meaningful
    assert _is_chunk_meaningful(
        _make_doc("This is meaningful content here"),
        doc_type="academic"
    )


def test_filter_short_text_default_doctype():
    """短於 10 字元、非 resume/slides、過濾。"""
    from processor.rag_processor import _is_chunk_meaningful
    assert not _is_chunk_meaningful(_make_doc("PhD"), doc_type="academic")
    assert not _is_chunk_meaningful(_make_doc("Hello"), doc_type="academic")


# ─────────────────── 修正 2: markdown 噪聲過濾（2 個）───────────────────


def test_filter_markdown_noise_only():
    """`## Summary\\n---` 是 14 字元、實質 7 字元、過濾。"""
    from processor.rag_processor import _is_chunk_meaningful
    assert not _is_chunk_meaningful(
        _make_doc("## Summary\n---"),
        doc_type="academic"
    )


def test_filter_separator_lines():
    """純分隔線（實質 0 字元）過濾。"""
    from processor.rag_processor import _is_chunk_meaningful
    assert not _is_chunk_meaningful(_make_doc("* * *"), doc_type="academic")
    assert not _is_chunk_meaningful(_make_doc("---"), doc_type="academic")
    assert not _is_chunk_meaningful(_make_doc("***"), doc_type="academic")


# ─────────────────── 修正 4: 履歷防誤殺（2 個）───────────────────


def test_resume_keeps_short_skill_keyword():
    """doc_type='resume' 保留 Python / Docker / Golang 等技能詞（6 字元）。"""
    from processor.rag_processor import _is_chunk_meaningful
    assert _is_chunk_meaningful(_make_doc("Python"), doc_type="resume")
    assert _is_chunk_meaningful(_make_doc("Docker"), doc_type="resume")
    assert _is_chunk_meaningful(_make_doc("Golang"), doc_type="resume")


def test_slides_keeps_short_keyword_threshold_3():
    """doc_type='slides' 放寬到 ≥ 3 字元、3 字元保留 / 2 字元過濾。"""
    from processor.rag_processor import _is_chunk_meaningful
    assert _is_chunk_meaningful(_make_doc("HVDC"), doc_type="slides")
    assert _is_chunk_meaningful(_make_doc("GPU"), doc_type="slides")    # 3 字元保留
    assert not _is_chunk_meaningful(_make_doc("AI"), doc_type="slides")  # 2 字元過濾


# ─────────────────── 修正 4: 結構化資訊保留（3 個）───────────────────


def test_keep_email_regardless_length():
    """含 email 保留（不論 doc_type / 不論長度）。"""
    from processor.rag_processor import _is_chunk_meaningful
    assert _is_chunk_meaningful(_make_doc("x@y.com"), doc_type="academic")
    assert _is_chunk_meaningful(_make_doc("john.doe@example.com"), doc_type="academic")


def test_keep_url_regardless_length():
    """含 url 保留。"""
    from processor.rag_processor import _is_chunk_meaningful
    assert _is_chunk_meaningful(
        _make_doc("https://example.com"),
        doc_type="academic"
    )
    assert _is_chunk_meaningful(_make_doc("https://x.io"), doc_type="academic")


def test_keep_phone_regardless_length():
    """含電話保留。"""
    from processor.rag_processor import _is_chunk_meaningful
    assert _is_chunk_meaningful(
        _make_doc("+886-912-345678"),
        doc_type="academic"
    )
    assert _is_chunk_meaningful(
        _make_doc("0912345678"),
        doc_type="academic"
    )

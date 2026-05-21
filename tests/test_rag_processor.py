"""Phase 4.7d Commit 15-1：rag_processor chunk 優化測試。

涵蓋 A（空 chunk 跳過）+ B（Context 前綴）+ D（短文合併）+ helper
_extract_section_title / _try_merge_text_items / _SHORT_DOC_TYPES。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from processor.rag_processor import RagProcessor, _SHORT_DOC_TYPES  # noqa: E402


def _proc():
    # embedder 為 object()——本檔測試不觸發 vector store 建立
    return RagProcessor(embedder=object())


# ── A. 空 chunk 跳過 ──

def test_empty_summary_returns_none():
    node = {'summary': '', 'type': 'section'}
    result = _proc()._generate_md_content(node, 'paper/Section A/section')
    assert result is None


def test_summary_whitespace_returns_none():
    node = {'summary': '   \n  ', 'type': 'section'}
    result = _proc()._generate_md_content(node, 'paper/A/section')
    assert result is None


def test_summary_with_content():
    node = {'summary': '這是一個摘要', 'type': 'section'}
    result = _proc()._generate_md_content(node, 'paper/A/section')
    assert result is not None
    assert '這是一個摘要' in result
    assert result.startswith('# paper/A/section\n')


# ── B. Context 前綴 ──

def test_text_with_doc_type_and_section():
    node = {'type': 'text', 'content': '工作內容描述'}
    result = _proc()._generate_md_content(
        node, 'paper/Working Experience/section/0/text',
        doc_type='resume', section_title='Working Experience',
    )
    assert 'Context: resume > Working Experience\n' in result
    assert '工作內容描述' in result


def test_no_context_when_no_doc_type():
    node = {'type': 'text', 'content': '一般內容'}
    result = _proc()._generate_md_content(
        node, 'paper/A/section/0/text'
    )
    # 沒給 doc_type / section_title → 不加 Context 行（向下相容）
    assert 'Context:' not in result
    assert '一般內容' in result


def test_context_only_doc_type():
    """有 doc_type 但無 section_title 時、Context 只含 doc_type"""
    node = {'type': 'text', 'content': '內容'}
    result = _proc()._generate_md_content(
        node, 'paper/A/section/0/text', doc_type='resume',
    )
    assert 'Context: resume\n' in result


# ── _extract_section_title ──

def test_extract_section_only():
    key = 'DeHunt Resume/Working Experience/section'
    assert _proc()._extract_section_title(key) == 'Working Experience'


def test_extract_text_item():
    key = 'DeHunt Resume/Working Experience/section/0/text'
    assert _proc()._extract_section_title(key) == 'Working Experience'


def test_extract_nested_children():
    key = 'DeHunt Resume/Working Experience/VIEWTRIX/section'
    assert _proc()._extract_section_title(key) == 'Working Experience > VIEWTRIX'


def test_extract_empty_key():
    assert _proc()._extract_section_title('') == ''


def test_extract_single_segment():
    assert _proc()._extract_section_title('paper_title') == ''


# ── _SHORT_DOC_TYPES registry ──

def test_short_doc_types_include_short_kinds():
    assert 'resume' in _SHORT_DOC_TYPES
    assert 'slides' in _SHORT_DOC_TYPES
    assert 'news' in _SHORT_DOC_TYPES
    assert 'web' in _SHORT_DOC_TYPES


def test_short_doc_types_exclude_long_kinds():
    assert 'academic' not in _SHORT_DOC_TYPES
    assert 'technical' not in _SHORT_DOC_TYPES
    assert 'book' not in _SHORT_DOC_TYPES


# ── _try_merge_text_items ──

def test_merge_multiple_text_items():
    section = {
        'title': 'Working Experience',
        'translated_title': '工作經歷',
        'content': [
            {'type': 'text', 'translated_content': '職位：CTO',
             'content': 'Role: CTO'},
            {'type': 'text', 'translated_content': '任期：2020-2025',
             'content': 'Tenure: 2020-2025'},
            {'type': 'text', 'translated_content': '職責：技術領導',
             'content': 'Responsibilities: tech lead'},
        ]
    }
    tree = {'title': 'XYZ Resume', 'translated_title': '張三履歷',
            'sections': [section]}

    result = _proc()._try_merge_text_items(section, tree, 'resume', 0)
    assert result is not None
    merged_key, full_md = result
    assert '_merged' in merged_key
    assert 'Context: resume > 工作經歷' in full_md
    assert '職位：CTO' in full_md
    assert '任期：2020-2025' in full_md
    assert '職責：技術領導' in full_md


def test_single_text_item_not_merged():
    section = {
        'title': 'A',
        'content': [{'type': 'text', 'content': 'only one'}],
    }
    tree = {'title': 'paper', 'sections': [section]}
    result = _proc()._try_merge_text_items(section, tree, 'resume', 0)
    assert result is None  # 只 1 個、不合併


def test_empty_section_returns_none():
    section = {'title': 'Empty', 'content': []}
    tree = {'title': 'paper', 'sections': [section]}
    result = _proc()._try_merge_text_items(section, tree, 'resume', 0)
    assert result is None


def test_merge_with_nested_child():
    """合併 nested child section 的 text items、merged_key 應含 parent path"""
    child = {
        'title': 'VIEWTRIX',
        'translated_title': 'VIEWTRIX 公司',
        'content': [
            {'type': 'text', 'translated_content': '職位 A', 'content': 'Role A'},
            {'type': 'text', 'translated_content': '職位 B', 'content': 'Role B'},
        ]
    }
    parent_section = {
        'title': 'Working Experience',
        'translated_title': '工作經歷',
        'children': [child],
    }
    tree = {'title': 'paper', 'translated_title': '張三履歷',
            'sections': [parent_section]}

    result = _proc()._try_merge_text_items(child, tree, 'resume', 0, ch_idx=0)
    assert result is not None
    merged_key, full_md = result
    # 應含 parent + child 路徑
    assert '工作經歷' in merged_key
    assert 'VIEWTRIX 公司' in merged_key
    assert '職位 A' in full_md
    assert '職位 B' in full_md

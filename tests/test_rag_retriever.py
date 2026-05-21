"""Phase 4.7d Commit 15-2：rag_retriever section title construction tests。

純測 `_build_section_title` 的 paper_title 前綴邏輯。不測 retrieve_with_context
（涉及 vector store / EmbeddingModel、需更重 fixture；本 commit 範圍只動字串拼裝）。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag_retriever import RagRetriever  # noqa: E402


def _retriever():
    return RagRetriever()


def test_build_section_title_with_paper_title():
    tree = {
        'translated_title': '張三履歷',
        'sections': [
            {'title': 'Working Experience', 'translated_title': '工作經歷'}
        ]
    }
    result = _retriever()._build_section_title(tree, '/sections/0')
    assert result == '張三履歷 > 工作經歷'


def test_build_section_title_with_child():
    tree = {
        'translated_title': '張三履歷',
        'sections': [{
            'title': 'Working Experience',
            'translated_title': '工作經歷',
            'children': [
                {'title': 'VIEWTRIX', 'translated_title': 'VIEWTRIX 公司'}
            ]
        }]
    }
    result = _retriever()._build_section_title(
        tree, '/sections/0/children/0'
    )
    assert result == '張三履歷 > 工作經歷 > VIEWTRIX 公司'


def test_build_section_title_no_paper_title_fallback():
    """無 translated_title 也無 title → 不加前綴"""
    tree = {
        'sections': [
            {'title': 'Working Experience', 'translated_title': '工作經歷'}
        ]
    }
    result = _retriever()._build_section_title(tree, '/sections/0')
    assert result == '工作經歷'  # 沒 paper title 時不加前綴


def test_build_section_title_paper_title_fallback_to_title():
    """無 translated_title、有 title → 用 title 當 paper 前綴"""
    tree = {
        'title': 'DeHunt Resume',
        'sections': [
            {'title': 'Working Experience'}  # 無 translated_title
        ]
    }
    result = _retriever()._build_section_title(tree, '/sections/0')
    assert result == 'DeHunt Resume > Working Experience'


def test_build_section_title_invalid_path():
    """無效 path → fallback 仍含 paper_title 前綴"""
    tree = {'translated_title': '張三履歷', 'sections': []}
    result = _retriever()._build_section_title(tree, '/invalid/path')
    assert '張三履歷' in result
    assert '章節' in result

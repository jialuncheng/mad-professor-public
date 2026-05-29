"""FE-AESTHETICS HOTFIX-1 專屬靜態測試"""
from pathlib import Path

STATIC_HTML = (Path(__file__).parent.parent / 'static' / 'index.html').read_text(encoding='utf-8')


def test_hotfix_normalize_academic_header_function_exists():
    """HOTFIX-1：index.html 應定義 normalizeAcademicHeader 自癒函數並在 fetchContent 中呼叫"""
    assert 'function normalizeAcademicHeader' in STATIC_HTML, \
        '應在 index.html 內定義 normalizeAcademicHeader 自癒相容函數'
    assert 'normalizeAcademicHeader()' in STATIC_HTML, \
        '應在 fetchContent 中調用 normalizeAcademicHeader()'

"""Phase 4.7d Commit 1：md_restore title 三軸融合決策樹單元測試。

對應 v2 §4.1 25 狀況決策樹的主要分支；不測 25/25（過度）、只測**設計關鍵點**：
resume 短路、黑名單、both_agree、pdf_metadata（v1 寫錯的 #15）、domain 仲裁、全空 fallback。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from processor.md_restore_processor import (
    _resolve_title,
    _title_in_blacklist,
    _title_sim,
    _dom_match,
    _tokenize_for_domain,
    # Commit 2
    _resolve_authors,
    _resolve_date,
    _resolve_venue,
    _resolve_doi,
    _resolve_keywords,
    _resolve_candidate_extras,
    _render_header_en,
    _render_header_zh,
    # Commit 3
    _resolve_abstract,
)


def _field(value, source='llm_page1'):
    return {'value': value, 'source': source,
            'confidence': 'high', 'alternates': {}}


def _meta(title=None, source=None, translated=None, candidate=None):
    """構造 metadata schema v2 樣式 dict（只放本測會用到的欄位）。"""
    m = {}
    if title is not None or source is not None:
        m['title'] = {'value': title, 'source': source,
                      'confidence': 'high', 'alternates': {}}
    if translated is not None:
        m['translated_title'] = {'value': translated, 'source': source,
                                 'confidence': 'high', 'alternates': {}}
    if candidate is not None:
        m['candidate_name'] = {'value': candidate, 'source': 'llm_page1',
                               'confidence': 'high', 'alternates': {}}
    return m


# ── helper functions ──
def test_blacklist_exact_match():
    assert _title_in_blacklist("Contents")
    assert _title_in_blacklist("目錄")
    assert _title_in_blacklist("PowerPoint Presentation")
    assert _title_in_blacklist("Resume")
    assert not _title_in_blacklist("AlphaFold-2: Improved Structure Prediction")


def test_blacklist_pattern_page_number():
    assert _title_in_blacklist("第 1 頁")
    assert _title_in_blacklist("Page 5")
    assert _title_in_blacklist("Slide 12")
    assert _title_in_blacklist("第 3 章")


def test_title_sim_equal_and_contains():
    assert _title_sim("AlphaFold", "AlphaFold")
    assert _title_sim("AlphaFold-2", "AlphaFold-2: Improved Structure Prediction")
    assert _title_sim("AlphaFold", "ALPHAFOLD")  # casefold
    assert not _title_sim("AlphaFold", "BERT")


def test_dom_match_chinese_ngram():
    # domain 與 value 都中文、有 2-gram 交集
    assert _dom_match("高壓直流系統架構", "電力電子技術 - 高壓直流系統架構")
    # 完全無交集
    assert not _dom_match("貓咪行為學", "電力電子技術 - 高壓直流系統架構")


def test_dom_match_empty_domain_returns_false():
    assert not _dom_match("Anything", "")


# ── _resolve_title 決策樹 ──

def test_resume_candidate_name_shortcut():
    """#1：resume + candidate_name → 短路取 candidate_name"""
    m = _meta(title="XDeHunt", source="llm_page1", candidate="DeHunt")
    en, zh, log = _resolve_title({'title': 'XDeHunt'}, m, 'resume', '')
    assert en == 'DeHunt' and zh == 'DeHunt'
    assert 'resume candidate_name' in log


def test_raw_blacklist_metadata_wins_llm():
    """#12：raw 在黑名單 + metadata=llm_page1 → metadata 勝"""
    m = _meta(title="800 VDC Architecture for AI Infrastructure", source="llm_page1")
    en, zh, log = _resolve_title({'title': 'Contents'}, m, 'technical', '')
    assert en.startswith("800 VDC")
    assert 'raw blacklisted' in log


def test_raw_blacklist_metadata_wins_slides():
    """#22 特化：slides 第 N 頁 → metadata 勝"""
    m = _meta(title="AI 基礎建設架構", source="llm_page1")
    en, zh, log = _resolve_title({'title': '第 1 頁'}, m, 'slides', '')
    assert en == "AI 基礎建設架構"
    assert 'raw blacklisted' in log


def test_pdf_metadata_untrustworthy_raw_wins():
    """#15（baron 核心觀察）：raw 合法 + metadata.source=pdf_metadata + 不 sim → raw 勝"""
    m = _meta(title="Microsoft Office User", source="pdf_metadata")
    en, zh, log = _resolve_title(
        {'title': 'Deep Learning for Protein Folding'}, m, 'academic', ''
    )
    assert en == 'Deep Learning for Protein Folding'
    assert 'pdf_meta untrustworthy' in log


def test_both_agree_metadata_wins():
    """#9：source=both_agree → metadata 勝"""
    m = _meta(title="AlphaFold-2", source="both_agree", translated="阿爾法摺疊 2")
    en, zh, log = _resolve_title(
        {'title': 'AlphaFold-2', 'translated_title': '阿爾法摺疊 2'},
        m, 'academic', ''
    )
    assert en == 'AlphaFold-2'
    assert zh == '阿爾法摺疊 2'
    assert 'both_agree' in log


def test_llm_sim_raw_metadata_wins():
    """#11：raw≈metadata 且 source=llm_page1 → metadata（較規範）"""
    m = _meta(title="AlphaFold-2: Improved Structure Prediction",
              source="llm_page1")
    en, zh, log = _resolve_title({'title': 'AlphaFold-2'}, m, 'academic', '')
    assert en.startswith('AlphaFold-2')
    assert 'sim raw' in log


def test_domain_arbitration_metadata_match():
    """#13a：兩者皆合法、不 sim、domain 偏向 metadata → 取 metadata"""
    m = _meta(title="800 VDC Architecture", source="llm_page1")
    en, zh, log = _resolve_title(
        {'title': 'User Guide'}, m, 'technical',
        domain='電力電子技術 - 800 VDC 架構',
    )
    assert en == '800 VDC Architecture'
    assert 'dom match M' in log or 'dom both match' in log


def test_domain_arbitration_raw_match():
    """#13b：兩者皆合法、不 sim、domain 偏向 raw → 取 raw"""
    m = _meta(title="Some Generic Title", source="llm_page1")
    en, zh, log = _resolve_title(
        {'title': 'Bicycle Racing 2025'}, m, 'news',
        domain='體育新聞 - Bicycle Racing 賽事',
    )
    assert en == 'Bicycle Racing 2025'
    assert 'dom match raw' in log


def test_domain_arbitration_both_fail_take_raw():
    """#13c：兩者皆合法、不 sim、domain 為空 → 保守取 raw"""
    m = _meta(title="Quantum Cryptography Survey", source="llm_page1")
    en, zh, log = _resolve_title(
        {'title': 'Bicycle Racing 2025'}, m, 'academic', domain=''
    )
    assert en == 'Bicycle Racing 2025'
    assert 'dom both fail' in log or 'take raw' in log


def test_all_empty_fallback_to_filename():
    """#4：全空 → fallback 到 original_filename（去 .pdf）"""
    en, zh, log = _resolve_title(
        {'title': ''}, {}, 'academic', '',
        original_filename='800-vdc-architecture-for-ai.pdf',
        paper_uuid='uuid-xxx',
    )
    assert en == '800-vdc-architecture-for-ai'
    assert 'fallback' in log


def test_all_empty_fallback_to_uuid_when_no_filename():
    """#4 邊界：original_filename 也空 → fallback paper_uuid"""
    en, zh, log = _resolve_title(
        {'title': ''}, {}, 'academic', '',
        original_filename=None, paper_uuid='abc-123',
    )
    assert en == 'abc-123'


def test_metadata_only_no_raw():
    """#5：raw 空、metadata 有 → metadata 勝"""
    m = _meta(title="My Paper", source="llm_page1", translated="我的論文")
    en, zh, log = _resolve_title({'title': ''}, m, 'academic', '')
    assert en == 'My Paper'
    assert zh == '我的論文'
    assert 'metadata only' in log


def test_raw_only_no_metadata():
    """#7：raw 有、metadata 空 → raw 勝"""
    en, zh, log = _resolve_title(
        {'title': 'A Paper', 'translated_title': '一篇論文'},
        {}, 'academic', ''
    )
    assert en == 'A Paper'
    assert zh == '一篇論文'
    assert 'raw only' in log


# ── Commit 2：authors 決策樹 ──

def test_resolve_authors_blacklist_all_dropped():
    """整陣列全黑名單 → drop M、保留 raw_authors_info"""
    m = {'authors': _field(['Microsoft Office User'], 'pdf_metadata')}
    data = {'authors_info': 'Alice & Bob\nMIT'}
    authors, keep_raw, log = _resolve_authors(data, m, 'academic')
    assert authors == []
    assert keep_raw is True
    assert 'all-blacklisted' in log


def test_resolve_authors_single_item_cleaned():
    """部分條目黑名單 → 剔除黑名單條目、保留乾淨條目"""
    m = {'authors': _field(['Microsoft Office User', 'Alice Chen'], 'llm_page1')}
    authors, keep_raw, log = _resolve_authors({}, m, 'academic')
    assert authors == ['Alice Chen']
    assert keep_raw is False


def test_resolve_authors_resume_skip():
    """resume 不顯示 authors"""
    m = {'authors': _field(['Anyone'], 'llm_page1')}
    authors, keep_raw, log = _resolve_authors({}, m, 'resume')
    assert authors == []
    assert keep_raw is False
    assert 'resume skip' in log


def test_resolve_authors_metadata_empty_keep_raw():
    """metadata 無 authors 但 raw 有 → 保留 raw"""
    authors, keep_raw, log = _resolve_authors(
        {'authors_info': 'Alice; Bob'}, {}, 'academic'
    )
    assert authors == []
    assert keep_raw is True


# ── Commit 2：date 決策樹 ──

def test_resolve_date_pdf_metadata_dropped():
    """v2 §4.3 #4：pdf_metadata 來源永遠丟"""
    m = {'publication_date': _field('2024-01-15', 'pdf_metadata')}
    date, log = _resolve_date(m)
    assert date == ''
    assert 'creation_date' in log


def test_resolve_date_future_blacklisted():
    """未來日期視為錯誤"""
    m = {'publication_date': _field('2099-12-31', 'llm_page1')}
    date, log = _resolve_date(m)
    assert date == ''
    assert 'blacklisted' in log


def test_resolve_date_llm_page1_kept():
    """llm_page1 抽到正常日期 → 保留"""
    m = {'publication_date': _field('2024-05-20', 'llm_page1')}
    date, log = _resolve_date(m)
    assert date == '2024-05-20'


# ── Commit 2：venue 決策樹 ──

def test_resolve_venue_priority_journal_first():
    """journal_or_conference > publisher > organization"""
    m = {
        'journal_or_conference': _field('Nature', 'llm_page1'),
        'publisher': _field('Springer', 'llm_page1'),
        'organization': _field('MIT', 'llm_page1'),
    }
    v, field, src = _resolve_venue(m)
    assert v == 'Nature'
    assert field == 'journal_or_conference'


def test_resolve_venue_pdf_metadata_skipped():
    """pdf_metadata 來源不採"""
    m = {
        'journal_or_conference': _field('Some Junk Subject', 'pdf_metadata'),
        'publisher': _field('NVIDIA', 'llm_page1'),
    }
    v, field, src = _resolve_venue(m)
    assert v == 'NVIDIA'
    assert field == 'publisher'


def test_resolve_venue_label_blacklist():
    """N/A / Unknown / TBD 視為空"""
    m = {'journal_or_conference': _field('N/A', 'llm_page1')}
    v, field, src = _resolve_venue(m)
    assert v == ''


def test_resolve_venue_organization_as_list():
    """Phase 4.7d Commit 8：LLM 偶爾把 organization 回 list（多個機構名）
    → _coerce_to_str 取第一個非空字串元素，不再炸 AttributeError"""
    m = {'organization': _field(['NVIDIA', 'Mellanox'], 'llm_page1')}
    v, field, src = _resolve_venue(m)
    assert v == 'NVIDIA'
    assert field == 'organization'


def test_resolve_venue_organization_empty_list():
    """list 全空 → coerce 回 '' → 跳過該欄"""
    m = {'organization': _field(['', '  ', None], 'llm_page1')}
    v, field, src = _resolve_venue(m)
    assert v == ''


def test_resolve_doi_value_as_list():
    """DOI 偶爾被回 list → 取第一個非空、再走格式驗證"""
    m = {'doi': _field(['10.1038/nature12373', 'fallback'], 'llm_page1')}
    assert _resolve_doi(m) == '10.1038/nature12373'


def test_resolve_date_value_as_list():
    """publication_date 偶爾被回 list → 取第一個非空"""
    m = {'publication_date': _field(['2024-05-20', 'unknown'], 'llm_page1')}
    date, log = _resolve_date(m)
    assert date == '2024-05-20'


def test_resolve_title_metadata_as_list():
    """title.value 偶爾 list → 取第一個非空 → 走決策樹 #5（raw 空 + meta 有）"""
    m = {'title': {'value': ['真標題', '副名'], 'source': 'llm_page1',
                   'confidence': 'high', 'alternates': {}}}
    en, zh, log = _resolve_title({'title': ''}, m, 'academic', '')
    assert en == '真標題'


# ── Commit 2：DOI 驗證 ──

def test_resolve_doi_valid():
    m = {'doi': _field('10.1038/nature12373', 'llm_page1')}
    assert _resolve_doi(m) == '10.1038/nature12373'


def test_resolve_doi_invalid_format_dropped():
    m = {'doi': _field('not-a-real-doi', 'llm_page1')}
    assert _resolve_doi(m) == ''


def test_resolve_doi_empty():
    assert _resolve_doi({}) == ''


# ── Commit 2：keywords ──

def test_resolve_keywords_label_stripped():
    m = {'keywords': _field(['Keywords', 'AI', 'ML', 'deep learning'], 'llm_page1')}
    kws = _resolve_keywords(m)
    assert 'Keywords' not in kws
    assert kws == ['AI', 'ML', 'deep learning']


def test_resolve_keywords_empty():
    assert _resolve_keywords({}) == []


# ── Commit 2：candidate_extras ──

def test_resolve_candidate_extras_resume():
    m = {'organization': _field('Tesla', 'llm_page1')}
    extras = _resolve_candidate_extras(m, 'resume')
    assert extras == {'organization': 'Tesla'}


def test_resolve_candidate_extras_non_resume_empty():
    m = {'organization': _field('Tesla', 'llm_page1')}
    assert _resolve_candidate_extras(m, 'academic') == {}


# ── Commit 2：header rendering ──

def test_render_header_en_academic_full():
    h = _render_header_en(
        title='AlphaFold-2', doc_type='academic',
        authors_list=['Alice', 'Bob'], date='2024-05-20',
        venue='Nature', doi='10.1038/x', keywords=['AI'],
        candidate_extras={}, domain='Protein folding',
    )
    assert h.startswith('# AlphaFold-2')
    assert 'Authors' in h and 'Alice, Bob' in h
    assert 'Date' in h and '2024-05-20' in h
    assert 'Venue' in h and 'Nature' in h


def test_render_header_zh_academic_full():
    h = _render_header_zh(
        title_zh='阿爾法摺疊-2', doc_type='academic',
        authors_list=['Alice', 'Bob'], date='2024-05-20',
        venue='Nature', doi='', keywords=['人工智慧'],
        candidate_extras={}, domain='',
    )
    assert h.startswith('# 阿爾法摺疊-2')
    assert '作者' in h and 'Alice、Bob' in h
    assert '日期' in h and '2024-05-20' in h
    assert '出處' in h and 'Nature' in h
    assert 'DOI' not in h  # 缺項省略
    assert '關鍵字' in h and '人工智慧' in h


def test_render_header_resume_simplified():
    h_en = _render_header_en(
        title='DeHunt', doc_type='resume',
        authors_list=[], date='', venue='', doi='', keywords=[],
        candidate_extras={'organization': 'Tesla'},
        domain='半導體 SoC',
    )
    assert '# DeHunt' in h_en
    assert 'Organization' in h_en and 'Tesla' in h_en
    assert 'Domain' in h_en
    # resume 不渲染 Authors / Date / Venue
    assert 'Authors' not in h_en
    assert 'Date' not in h_en


def test_render_header_missing_fields_silently_omitted():
    h = _render_header_zh(
        title_zh='Some Title', doc_type='news',
        authors_list=[], date='', venue='', doi='', keywords=[],
        candidate_extras={}, domain='',
    )
    # 只有 title + 空行
    assert h.strip() == '# Some Title'


# ── Commit 3：abstract 雙語注入 ──

def _abstract_section(en, zh=None):
    """構造 sections[type=='abstract'] 結構（同 translate_processor 寫法）。"""
    item = {'type': 'text', 'content': en}
    if zh is not None:
        item['translated_content'] = zh
    return {'type': 'abstract', 'content': [item]}


def test_resolve_abstract_found_in_sections():
    """en + zh 都有 → 各取各的"""
    data = {'sections': [_abstract_section('English abstract.', '中文摘要。')]}
    en, zh, log = _resolve_abstract(data, 'academic')
    assert en == 'English abstract.'
    assert zh == '中文摘要。'
    assert 'found' in log


def test_resolve_abstract_translated_fallback_to_original():
    """有 en 但無 zh → zh fallback 為 en（避免中文版完全沒 abstract）"""
    data = {'sections': [_abstract_section('English only.')]}
    en, zh, log = _resolve_abstract(data, 'academic')
    assert en == 'English only.'
    assert zh == 'English only.'


def test_resolve_abstract_news_skipped():
    """news doc_type → translate 階段已 skip、md_restore 也跳過"""
    data = {'sections': [_abstract_section('Should not be used.', '不應使用')]}
    en, zh, log = _resolve_abstract(data, 'news')
    assert en == '' and zh == ''
    assert 'no abstract' in log


def test_resolve_abstract_resume_skipped():
    data = {'sections': [_abstract_section('x', 'x')]}
    en, zh, log = _resolve_abstract(data, 'resume')
    assert en == '' and zh == ''


def test_resolve_abstract_no_section_in_sections():
    """sections 內無 abstract type → 回空"""
    data = {'sections': [{'type': 'introduction', 'content': []}]}
    en, zh, log = _resolve_abstract(data, 'academic')
    assert en == '' and zh == ''
    assert 'no abstract section' in log


def test_render_header_en_with_abstract():
    h = _render_header_en(
        title='Paper', doc_type='academic',
        authors_list=['A'], date='2024', venue='', doi='', keywords=[],
        candidate_extras={}, domain='', abstract='Lorem ipsum abstract.',
    )
    assert '## Abstract' in h
    assert 'Lorem ipsum abstract.' in h


def test_render_header_zh_with_abstract():
    h = _render_header_zh(
        title_zh='論文', doc_type='academic',
        authors_list=[], date='', venue='', doi='', keywords=[],
        candidate_extras={}, domain='', abstract='中文摘要內容。',
    )
    assert '## 摘要' in h
    assert '中文摘要內容。' in h


def test_render_header_resume_no_abstract_block():
    """resume header 即使傳 abstract 也不渲染 ## 摘要"""
    h = _render_header_zh(
        title_zh='姓名', doc_type='resume',
        authors_list=[], date='', venue='', doi='', keywords=[],
        candidate_extras={'organization': 'Tesla'}, domain='',
        abstract='不該出現',
    )
    assert '## 摘要' not in h
    assert '不該出現' not in h

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
)


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

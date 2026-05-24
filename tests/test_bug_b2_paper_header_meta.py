"""RAG-1 BUG-B2：後端 blockquote → list + 前端 paper-header-meta CSS pytest
（依評估 v4 §B Bug 10 / ui-fixes-batch B8）。

涵蓋（後端 + 前端跨檔同 commit、混合 bug）：

後端（processor/md_restore_processor.py）：
- _render_header_en：academic path `>` → `-` list + `<div class="paper-header-meta">` wrap
- _render_header_zh：academic path 同上（中文 label）
- resume path 100% 未動（v4 評估範圍外、`>` blockquote 保留）

前端（static/index.html）：
- @media screen hide #paper-content > h1:first-child + > .paper-header-meta
- 確保 @media print 不被誤套（class hook 穩定、舊 paper 仍可顯示）
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from processor.md_restore_processor import _render_header_en, _render_header_zh  # noqa: E402

STATIC_HTML = (ROOT / 'static' / 'index.html').read_text(encoding='utf-8')


# ─────────────────── 後端 academic path：- list + wrap ───────────────────


def test_render_header_en_academic_uses_dash_list_and_wrap():
    """B10 後端：英文 academic path 用 `- **Authors**`（不再 `> **Authors**`）+ 包進 paper-header-meta wrap。"""
    md = _render_header_en(
        title="Some Paper",
        doc_type="academic",
        authors_list=["Alice", "Bob"],
        date="2024-01",
        venue="ICML",
        doi="10.1234/xyz",
        keywords=["k1", "k2"],
        candidate_extras={},
        domain="ml",
    )
    # 不應再有 `> **Authors**` blockquote
    assert "> **Authors**" not in md, '英文 academic 不應再用 > blockquote'
    # 應有 `- **Authors**` list（5 條 meta_bits 全部）
    for label in ("Authors", "Date", "Venue", "DOI", "Keywords"):
        assert f"- **{label}**" in md, f'應有 `- **{label}**` list item'
    # wrap div 含 5 meta_bits
    assert '<div class="paper-header-meta">' in md
    assert '</div>' in md
    # wrap 順序：div open → bits → div close
    open_idx = md.find('<div class="paper-header-meta">')
    close_idx = md.find('</div>')
    authors_idx = md.find('- **Authors**')
    assert open_idx < authors_idx < close_idx, 'wrap 順序：<div> → meta-bits → </div>'


def test_render_header_zh_academic_uses_dash_list_and_wrap():
    """B10 後端：中文 academic path 用 `- **作者**`（不再 `> **作者**`）+ 包進 paper-header-meta wrap。"""
    md = _render_header_zh(
        title_zh="某論文",
        doc_type="academic",
        authors_list=["甲", "乙"],
        date="2024-01",
        venue="某會議",
        doi="10.1234/xyz",
        keywords=["關鍵字1", "關鍵字2"],
        candidate_extras={},
        domain="機器學習",
    )
    assert "> **作者**" not in md, '中文 academic 不應再用 > blockquote'
    for label in ("作者", "日期", "出處", "DOI", "關鍵字"):
        assert f"- **{label}**" in md, f'應有 `- **{label}**` list item'
    assert '<div class="paper-header-meta">' in md
    assert '</div>' in md


# ─────────────────── 後端 resume path：100% 未動 ───────────────────


def test_render_header_en_resume_blockquote_preserved():
    """B10 禁區：resume path `>` blockquote 100% 未動（v4 評估範圍外）。"""
    md = _render_header_en(
        title="John Doe Resume",
        doc_type="resume",
        authors_list=[],
        date="",
        venue="",
        doi="",
        keywords=[],
        candidate_extras={"organization": "Acme Corp"},
        domain="software",
    )
    # resume 路徑仍用 `> **Organization**` / `> **Domain**` blockquote
    assert "> **Organization**: Acme Corp" in md, 'resume English 應保留 > blockquote 格式（範圍外）'
    assert "> **Domain**: software" in md
    # resume 路徑 NOT 包 paper-header-meta wrap（評估範圍外）
    assert '<div class="paper-header-meta">' not in md, (
        'resume path 不應加 paper-header-meta wrap（v4 評估範圍外、禁區）'
    )


def test_render_header_zh_resume_blockquote_preserved():
    """B10 禁區：resume 中文 path 同上、`>` 保留、不加 wrap。"""
    md = _render_header_zh(
        title_zh="王某履歷",
        doc_type="resume",
        authors_list=[],
        date="",
        venue="",
        doi="",
        keywords=[],
        candidate_extras={"organization": "某公司"},
        domain="軟體",
    )
    assert "> **機構**：某公司" in md, 'resume 中文應保留 > blockquote 格式（範圍外）'
    assert "> **領域**：軟體" in md
    assert '<div class="paper-header-meta">' not in md


# ─────────────────── 後端 academic：缺項時不 wrap ───────────────────


def test_render_header_en_academic_no_meta_no_wrap():
    """B10 邊界：academic 但 meta_bits 全空時、不應產生空的 wrap div。"""
    md = _render_header_en(
        title="Lonely Paper",
        doc_type="academic",
        authors_list=[],
        date="",
        venue="",
        doi="",
        keywords=[],
        candidate_extras={},
        domain="",
    )
    # meta_bits 為空時、不應有 paper-header-meta wrap
    assert '<div class="paper-header-meta">' not in md, (
        '空 meta_bits 不應產生空 wrap div'
    )
    # title 仍應正常輸出
    assert "# Lonely Paper" in md


# ─────────────────── 前端 CSS @media screen hide ───────────────────


def test_b10_frontend_media_screen_hides_h1_and_header_meta():
    """B10 前端：@media screen 區塊 hide #paper-content > h1:first-child 與 > .paper-header-meta、
    @media print 模式不受此規則影響。"""
    # @media screen { #paper-content > h1:first-child, #paper-content > .paper-header-meta { display: none; } }
    pat = re.compile(
        r'@media\s+screen\s*\{[^}]*'
        r'#paper-content\s*>\s*h1:first-child\s*,\s*'
        r'#paper-content\s*>\s*\.paper-header-meta\s*\{[^}]*display:\s*none',
        re.DOTALL,
    )
    assert pat.search(STATIC_HTML), (
        '前端 CSS 應有 @media screen { #paper-content > h1:first-child, '
        '#paper-content > .paper-header-meta { display: none; } } 結構'
    )


def test_b10_frontend_class_hook_not_in_print_media():
    """B10 前端：hide 規則必須包在 @media screen、不能裸寫（否則列印也會 hide、破壞列印模式恢復標題契約）。"""
    # 找所有 #paper-content > .paper-header-meta { display: none } 出現的位置
    occurrences = [m.start() for m in re.finditer(
        r'#paper-content\s*>\s*\.paper-header-meta', STATIC_HTML)]
    assert occurrences, '應有 .paper-header-meta selector'

    # 第一個 occurrence 之前 200 字必須含 @media screen（保證在 media query 內）
    first = occurrences[0]
    context_before = STATIC_HTML[max(0, first - 200):first]
    assert '@media screen' in context_before, (
        'hide 規則必須包在 @media screen 內、避免影響 @media print 列印模式'
    )

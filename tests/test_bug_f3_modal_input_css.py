"""RAG-1 BUG-F3：.modal-input CSS pytest（2 個）。

涵蓋（依評估報告 v2 §B Bug 7 + ui-fixes-batch B5）：
- 補 .modal-input + input[type="text"] 廣義 CSS 樣式（R2 ship 時 HTML 用 class 但無 CSS）
- focus ring 用 color-mix 跨主題自動跟色（不寫死 rgba）
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STATIC_HTML = (ROOT / 'static' / 'index.html').read_text(encoding='utf-8')


def test_bug7_modal_input_css_defined():
    """Bug 7：.modal-box .modal-input + .modal-box input[type="text"] 雙 selector CSS 樣式存在、
    含 design tokens（--btn-h / --space-3 / --radius-md / --color-divider / --color-bg / --color-text）。"""
    # 雙 selector 同時宣告（class + 廣義）
    pat = re.compile(
        r'\.modal-box\s+\.modal-input\s*,\s*\.modal-box\s+input\[type="text"\]\s*\{',
        re.DOTALL,
    )
    assert pat.search(STATIC_HTML), (
        '.modal-box .modal-input 與 .modal-box input[type="text"] 必須以雙 selector 同時宣告'
        '（既有 #tag-input 用 class、未來新 input 走廣義）'
    )

    # base rule body 含必要 design tokens
    # 取整個 .modal-box .modal-input CSS rule 內容
    body_pat = re.compile(
        r'\.modal-box\s+\.modal-input\s*,\s*\.modal-box\s+input\[type="text"\]\s*\{([^}]*)\}',
        re.DOTALL,
    )
    m = body_pat.search(STATIC_HTML)
    assert m, '.modal-input rule body 取得失敗'
    body = m.group(1)
    for token in (
        'width: 100%',
        'height: var(--btn-h)',
        'padding: 0 var(--space-3)',
        'border: 1px solid var(--color-divider)',
        'border-radius: var(--radius-md)',
        'background: var(--color-bg)',
        'color: var(--color-text)',
        'box-sizing: border-box',
    ):
        assert token in body, (
            f'.modal-input rule body 應含 `{token}` design token（跟 .modal-box select 對齊）'
        )


def test_bug7_modal_input_focus_uses_color_mix_cross_theme():
    """Bug 7 ui-fixes-batch B5 強化：focus ring 用 color-mix 跨主題自動跟色、不寫死 rgba()。"""
    # :focus 雙 selector
    pat = re.compile(
        r'\.modal-box\s+\.modal-input:focus\s*,\s*\.modal-box\s+input\[type="text"\]:focus\s*\{([^}]*)\}',
        re.DOTALL,
    )
    m = pat.search(STATIC_HTML)
    assert m, (
        '.modal-input:focus 與 input[type="text"]:focus 必須雙 selector 同時宣告'
    )
    body = m.group(1)

    # border-color 改 accent
    assert 'border-color: var(--color-accent)' in body, (
        'focus 應 border-color: var(--color-accent)'
    )

    # box-shadow 用 color-mix（跨主題跟色、不寫死 rgba）
    assert 'color-mix(' in body, (
        'focus ring 應用 color-mix() 跨主題跟色、不寫死 rgba()'
    )
    assert 'var(--color-accent)' in body, (
        'color-mix 內必須引用 var(--color-accent)、確保跟主題色同步'
    )

    # 不可有寫死的 rgba(59, 130, 246, ...) blue（Bug_Fix_Report 提議的寫死方式）
    assert 'rgba(59, 130, 246' not in body, (
        '不可寫死 rgba(59,130,246,...)（會跟非 blue accent 主題不一致）'
    )

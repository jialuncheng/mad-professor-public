"""RAG-1 BUG-F2：theme dropdown + ESC + Bug 11 P2-3 latent fix pytest（5 個）。

涵蓋（依評估報告 v2 §B Bug 2 + Bug 11）：
- Bug 11 P2-3 latent：#hashtag-autocomplete 不含 .ctx-popup class（避免被 closePopups 永久刪除）
- Bug 2 A5：dropdownAPI IIFE 暴露 addTheme/getThemeLabel API、TDZ-aware 3 段拆分
- Bug 2 A5：upload handler change listener 註冊位置在 dropdownAPI IIFE 之後
- Bug 2 A5：L1786 outer labels 已 dedup（刪除、統一由 IIFE 內 themeLabels 管理）
- Bug 2 A6：ESC handler 先處理 popup（含 .ctx-popup）、再處理 modal、一次只關一層
"""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STATIC_HTML = (ROOT / 'static' / 'index.html').read_text(encoding='utf-8')


# ─────────────────── Bug 11：P2-3 hashtag-autocomplete 不含 .ctx-popup ───────────────────


def test_bug11_hashtag_autocomplete_not_ctx_popup():
    """Bug 11 latent fix：#hashtag-autocomplete HTML 用 class="hashtag-popup"、不含 .ctx-popup。"""
    # 不應有 class="ctx-popup hashtag-popup" 組合
    assert not re.search(
        r'id="hashtag-autocomplete"[^>]*class="[^"]*ctx-popup[^"]*"',
        STATIC_HTML,
    ), '#hashtag-autocomplete 不應含 .ctx-popup class（會被 closePopups 永久 .remove()）'
    # 應該有 class="hashtag-popup" 單獨存在
    assert re.search(
        r'id="hashtag-autocomplete"[^>]*class="hashtag-popup"',
        STATIC_HTML,
    ), '#hashtag-autocomplete 應為 class="hashtag-popup"（standalone、不依賴 ctx-popup base style）'


# ─────────────────── Bug 2 A5：dropdownAPI IIFE 暴露 + TDZ 3 段拆分 ───────────────────


def test_bug2_a5_dropdown_api_iife_exposed():
    """Bug 2 A5：dropdownAPI IIFE 宣告 + window 暴露 + addTheme / getThemeLabel API 存在。"""
    # const dropdownAPI = (() => { ... })()
    assert re.search(
        r'const\s+dropdownAPI\s*=\s*\(\(\)\s*=>\s*\{',
        STATIC_HTML,
    ), '應有 const dropdownAPI = (() => {...})() IIFE 宣告'

    # window.dropdownAPI 暴露
    assert 'window.dropdownAPI = dropdownAPI;' in STATIC_HTML, (
        '應 window.dropdownAPI = dropdownAPI 對外暴露'
    )

    # IIFE 內 return addTheme + getThemeLabel
    assert re.search(
        r'addTheme\s*\(\s*name\s*,\s*label\s*\)\s*\{',
        STATIC_HTML,
    ), 'dropdownAPI 應 return addTheme(name, label) method'
    assert re.search(
        r'getThemeLabel\s*\(\s*name\s*\)\s*\{',
        STATIC_HTML,
    ), 'dropdownAPI 應 return getThemeLabel(name) method'

    # themeLabels 用 Object.fromEntries(THEMES) 統一管理
    assert 'Object.fromEntries(THEMES)' in STATIC_HTML, (
        'themeLabels 應由 Object.fromEntries(THEMES) 生成、跟 THEMES 同步'
    )


def test_bug2_a5_tdz_three_segment_savedTheme():
    """Bug 2 A5 TDZ 拆分：savedTheme 分 3 段執行、IIFE 之後 sync dropdown 顯示值。"""
    # 第一段標記
    assert '【第一段】TDZ-aware 拆分：dropdownAPI IIFE 之前' in STATIC_HTML, (
        '第一段註記應存在（IIFE 之前、只套用 themeLink）'
    )
    # 第二段：dropdownAPI IIFE
    assert '【第二段】TDZ-aware：dropdownAPI IIFE' in STATIC_HTML, (
        '第二段註記應存在（dropdownAPI IIFE）'
    )
    # 第三段標記 + IIFE 之後 savedTheme sync
    assert '【第三段】TDZ-aware：dropdownAPI IIFE 之後' in STATIC_HTML, (
        '第三段註記應存在（IIFE 之後、sync dropdown 顯示值）'
    )

    # 第三段內必含 dropdownAPI.addTheme(savedTheme) + getThemeLabel(savedTheme)
    pat = re.compile(
        r'第三段.*?if\s*\(savedTheme\)\s*\{[^}]*dropdownAPI\.addTheme\(savedTheme\)[^}]*dropdownAPI\.getThemeLabel\(savedTheme\)',
        re.DOTALL,
    )
    assert pat.search(STATIC_HTML), (
        '第三段 if (savedTheme) 區塊應含 dropdownAPI.addTheme + getThemeLabel 同步'
    )

    # 順序驗證：第一段 dropdownAPI 出現位置 < IIFE 宣告 < 第三段
    # 用簡單字串 index 順序
    idx_first = STATIC_HTML.find('【第一段】TDZ-aware 拆分：dropdownAPI IIFE 之前')
    idx_iife = STATIC_HTML.find('const dropdownAPI = (() =>')
    idx_third = STATIC_HTML.find('【第三段】TDZ-aware：dropdownAPI IIFE 之後')
    assert 0 < idx_first < idx_iife < idx_third, (
        f'順序應為【第一段】< IIFE 宣告 <【第三段】；'
        f'目前 first={idx_first} / iife={idx_iife} / third={idx_third}'
    )


def test_bug2_a5_upload_handler_after_iife():
    """Bug 2 A5：theme-upload-input change handler 註冊位置在 dropdownAPI IIFE 之後（防 TDZ）。"""
    # change handler 註冊行
    pat_handler = re.compile(
        r"document\.getElementById\(['\"]theme-upload-input['\"]\)\.addEventListener\(['\"]change['\"]"
    )
    match = pat_handler.search(STATIC_HTML)
    assert match, 'theme-upload-input change handler 應存在'

    idx_iife = STATIC_HTML.find('const dropdownAPI = (() =>')
    idx_handler = match.start()
    assert idx_iife < idx_handler, (
        f'theme-upload-input change handler 註冊位置必須在 dropdownAPI IIFE 之後；'
        f'目前 iife={idx_iife} / handler={idx_handler}'
    )

    # handler body 應用 dropdownAPI.addTheme + getThemeLabel
    # 從 handler 註冊位置往後找 dropdownAPI 呼叫
    tail = STATIC_HTML[idx_handler:]
    assert 'dropdownAPI.addTheme(themeName)' in tail[:3000], (
        'upload handler body 應呼叫 dropdownAPI.addTheme(themeName)'
    )
    assert 'dropdownAPI.getThemeLabel(themeName)' in tail[:3000], (
        'upload handler body 應呼叫 dropdownAPI.getThemeLabel(themeName) 更新 dropdown 顯示'
    )


def test_bug2_a5_outer_labels_deduped():
    """Bug 2 A5：L1786 outer labels（const labels = { mies: ... }）已刪除、統一由 IIFE 內 themeLabels 管理。"""
    # 全檔不應再有 const labels = { mies: ... }
    assert not re.search(
        r'const\s+labels\s*=\s*\{\s*mies\s*:',
        STATIC_HTML,
    ), 'L1786 outer labels 應已 dedup 刪除（統一由 dropdownAPI IIFE 內 themeLabels 管理）'


# ─────────────────── Bug 2 A6：ESC 先 popup 再 modal ───────────────────


def test_bug2_a6_esc_handles_popup_first_then_modal():
    """Bug 2 A6：ESC handler 偵測 .ctx-popup 存在時優先 closePopups()、return；後才處理 modal。"""
    # 鎖定 modal ESC handler 區塊（用 "// ESC + Tab 焦點循環" 註記為錨）、不誤抓 chat-input keydown
    marker = '// ESC + Tab 焦點循環'
    idx = STATIC_HTML.find(marker)
    assert idx >= 0, '應有 "// ESC + Tab 焦點循環" 區塊註記'

    # 取該區塊 + 後續 1500 字（涵蓋 closeModal）
    block = STATIC_HTML[idx:idx + 1500]

    # 必含關鍵元素
    assert "if (e.key === 'Escape')" in block, (
        'ESC handler 應有 if (e.key === Escape) 統一入口'
    )
    assert "const hasPopup = document.querySelector('.ctx-popup')" in block, (
        '應先 const hasPopup = document.querySelector(.ctx-popup) 偵測'
    )
    assert 'if (hasPopup)' in block, (
        '應 if (hasPopup) 條件式內處理 popup'
    )

    # 順序：hasPopup → closePopups → 後接 closeModal（先 popup 再 modal）
    idx_hasPopup = block.find('if (hasPopup)')
    idx_closeModal = block.find('closeModal(open)')
    idx_closePopups_in_block = block.find('closePopups()', idx_hasPopup)
    assert 0 < idx_closePopups_in_block < idx_closeModal, (
        f'closePopups() 必須在 closeModal(open) 之前（先 popup 再 modal）；'
        f'hasPopup={idx_hasPopup} closePopups={idx_closePopups_in_block} closeModal={idx_closeModal}'
    )

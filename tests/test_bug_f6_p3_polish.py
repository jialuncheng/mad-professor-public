"""RAG-1 BUG-F6：P3 polish 落地 pytest（依評估 v3 §B C3 + C4 + C5 + C6 + C7）。

涵蓋：
- C3：useWebSearch 顯式宣告（已 ship 之 no-op 驗證）
- C4：~43 處 Phase 4.7 / RAG-1 R1/R2 / Commit-N ticket 編號註解全部清理
- C5：marked strikethrough hack 註解區塊改寫（含「何時可移除」條件）
- C6：chat-input focus listener 已刪（BUG-F4 A3.2 已 ship 之 no-op 驗證）
- C7：paper-menu-btn / folder menu-btn `⋯` 字元 → SVG + data-tip 遷移
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STATIC_HTML = (ROOT / 'static' / 'index.html').read_text(encoding='utf-8')
ICON_SPEC_MD = (ROOT / 'design' / 'docs' / 'icon-spec.md').read_text(encoding='utf-8')


# ─────────────────── C3：useWebSearch 顯式宣告（no-op 驗證）───────────────────


def test_c3_useWebSearch_explicit_declaration():
    """C3 no-op 驗證：useWebSearch 已顯式 `let useWebSearch = false;` 宣告於 script 全域變數區、
    跟 currentPaperId / isProcessing 同層級；本 commit 不需動作。"""
    assert re.search(
        r'^\s*let\s+useWebSearch\s*=\s*false\s*;',
        STATIC_HTML, re.MULTILINE,
    ), 'C3：useWebSearch 應有顯式 `let useWebSearch = false;` 宣告於 script 全域變數區'

    # 跟其他既有全域變數（currentPaperId / isProcessing）同檔同區段
    idx_useWeb = STATIC_HTML.find('let useWebSearch = false;')
    idx_currentPaperId = STATIC_HTML.find('let currentPaperId = null;')
    idx_isProcessing = STATIC_HTML.find('let isProcessing = false;')
    assert all(i > 0 for i in [idx_useWeb, idx_currentPaperId, idx_isProcessing]), (
        '三個全域變數宣告都應存在'
    )
    # 三個 let 應在彼此 200 字內（同個 script 區塊）
    block_span = max(idx_useWeb, idx_currentPaperId, idx_isProcessing) - \
                 min(idx_useWeb, idx_currentPaperId, idx_isProcessing)
    assert block_span < 200, (
        f'C3：三個 let 應在同一個全域變數宣告區（span={block_span}）'
    )


# ─────────────────── C4：~43 處 ticket 編號註解清理 ───────────────────


def test_c4_legacy_ticket_prefixes_cleaned():
    """C4：靜態文件不應再有以下 ticket 編號 prefix（除本 commit 自身的 BUG-F4/F5/F6 等近期參考）：
    - `Phase 4.7?` / `Phase 4.7c` / `Phase 4.7d Commit N`
    - `RAG-1 R1 子項 X` / `RAG-1 R2 子項 X`
    - `RAG-1 Phase 2 P2-3 §x.x.x` 等舊精確章節編號（保留 §x.x 通用引用）

    保留：BUG-F1~F6 / P2-3（章節級簡稱）/ components.md §11 等規範引用。
    """
    bad = []
    for i, line in enumerate(STATIC_HTML.split('\n'), 1):
        # 偵測 Phase 4.7（c/d/e/?）
        if re.search(r'Phase 4\.7[a-z?]?', line):
            bad.append(f'L{i} [Phase 4.7]: {line.strip()[:80]}')
        # 偵測 Phase 4.7d Commit N（17-1 / 11 等）
        if re.search(r'Commit \d+(-\d+[a-z]?)?', line):
            bad.append(f'L{i} [Commit-N]: {line.strip()[:80]}')
        # 偵測 RAG-1 R1 子項 / RAG-1 R2 子項 / RAG-1 R3 子項
        if re.search(r'RAG-1\s+R[1-9]\s+子項', line):
            bad.append(f'L{i} [RAG-1 RX 子項]: {line.strip()[:80]}')

    assert not bad, (
        'C4 殘留 ticket 編號 prefix：\n' + '\n'.join(bad[:20])
        + ('\n... (+ more)' if len(bad) > 20 else '')
    )


# ─────────────────── C5：marked strikethrough hack 註解改寫 ───────────────────


def test_c5_marked_strikethrough_comment_rewrite():
    """C5：marked.use({ ... del extension ... }) 上方註解應改寫為包含「為何」+「何時可移除」、
    不再含 `Phase 4.7? RAG-9 fix` ticket 編號。"""
    # 不應再有 `RAG-9 fix` 字眼
    assert 'RAG-9 fix' not in STATIC_HTML, (
        'C5：`RAG-9 fix` ticket 編號應改寫掉'
    )
    # 應有「為何」段
    assert '為何：marked.js' in STATIC_HTML, (
        'C5：應有「為何：marked.js ...」說明段'
    )
    # 應有「何時可移除」條件
    assert '何時可移除' in STATIC_HTML, (
        'C5：應有「何時可移除」條件段、明確未來移除觸發條件'
    )


# ─────────────────── C6：chat-input focus listener no-op ───────────────────


def test_c6_chat_input_focus_listener_removed():
    """C6 no-op 驗證：chat-input focus listener 應已被 BUG-F4 A3.2 刪除、本 commit 不需動作。"""
    # 不應再有 chat-input addEventListener('focus', () => { ... if (!currentPaperId) ... })
    assert not re.search(
        r"getElementById\(['\"]chat-input['\"]\)\.addEventListener\(['\"]focus['\"]",
        STATIC_HTML,
    ), 'C6：chat-input focus listener 應已刪除（BUG-F4 A3.2 已處理）'


# ─────────────────── C7：⋯ 字元 → SVG + data-tip ───────────────────


def test_c7_paper_menu_btn_svg_with_data_tip():
    """C7：paper-menu-btn HTML 從 `⋯` + `title="更多"` 遷移為 SVG 3-circle + `data-tip="文件選單"`。"""
    # 不應再有 paper-menu-btn 用 title="更多" + ⋯ 字元
    assert not re.search(
        r'<button[^>]*class="paper-menu-btn[^"]*"[^>]*title="更多"[^>]*>⋯<',
        STATIC_HTML,
    ), 'C7：paper-menu-btn 不應再用 title="更多" + ⋯ 字元'

    # 應該有 paper-menu-btn + data-tip="文件選單" + SVG 3-circle
    pat = re.compile(
        r'<button[^>]*class="paper-menu-btn[^"]*"[^>]*data-tip="文件選單"[^>]*>\s*<svg[^>]*>(.*?)</svg>\s*</button>',
        re.DOTALL,
    )
    m = pat.search(STATIC_HTML)
    assert m, (
        'C7：paper-menu-btn 應改為 <button class="paper-menu-btn ..." data-tip="文件選單"><svg>...</svg></button>'
    )
    # SVG 內含 3 個 circle
    circles = m.group(1).count('<circle')
    assert circles == 3, (
        f'C7：paper-menu-btn SVG 應含 3 個 <circle> 元素、目前 {circles} 個'
    )


def test_c7_folder_menu_btn_svg_with_data_tip():
    """C7：folder menu-btn（renderFolderTree 內 row.innerHTML 字串模板）
    從 `⋯` + `title="資料夾選單"` 遷移為 SVG 3-circle + `data-tip="資料夾選單"`。

    v3.1 line drift 校正：grep pattern 真實命中位置（非草稿行號）。
    """
    # 不應再有 menu-btn 用 title="資料夾選單" + ⋯ 字元
    assert not re.search(
        r'<button class="menu-btn"\s+title="資料夾選單">⋯<',
        STATIC_HTML,
    ), 'C7：folder menu-btn 不應再用 title="資料夾選單" + ⋯ 字元'

    # 應有 menu-btn + data-tip="資料夾選單" + SVG 3-circle
    pat = re.compile(
        r'<button class="menu-btn"\s+data-tip="資料夾選單"><svg[^>]*>(.*?)</svg></button>',
        re.DOTALL,
    )
    m = pat.search(STATIC_HTML)
    assert m, (
        'C7：folder menu-btn 應改為 <button class="menu-btn" data-tip="資料夾選單"><svg>...</svg></button>'
    )
    circles = m.group(1).count('<circle')
    assert circles == 3, (
        f'C7：folder menu-btn SVG 應含 3 個 <circle> 元素、目前 {circles} 個'
    )


# ─────────────────── C7 配套 design docs 更新 ───────────────────


def test_c7_icon_spec_doc_notes_bug_f6_migration():
    """C7 配套：design/docs/icon-spec.md §4 對 .paper-menu-btn / .menu-btn 應註明 BUG-F6 遷移。"""
    # icon-spec.md §4 對「更多」行應包含 BUG-F6 或 data-tip 字眼
    assert 'BUG-F6' in ICON_SPEC_MD or 'data-tip' in ICON_SPEC_MD, (
        'C7 配套：icon-spec.md §4 應註明 BUG-F6 C7 從 ⋯ 字元遷移到 SVG + data-tip 規範'
    )

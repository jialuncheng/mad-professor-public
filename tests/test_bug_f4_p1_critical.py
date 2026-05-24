"""RAG-1 BUG-F4：P1 critical 4 項落地 pytest（依評估 v3 §B A1+A2+A3+A4）。

涵蓋：
- A1：trackProgress 完成路徑改用 renderTitleHeader（保留 multi-row 結構）
- A2：empty-state 預設顯示反轉（重整時中欄顯示「從左側選擇文件」）
- A3：customPrompt 新增（#prompt-modal DOM + customPrompt 函式 + window 暴露）
- A3.2：全 native dialog（alert / confirm / prompt）替換為 custom*
- A4：closeBizPopups 函式 + 第二個 document click listener 已刪除、統一走 closePopups
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STATIC_HTML = (ROOT / 'static' / 'index.html').read_text(encoding='utf-8')


# ─────────────────── A1：trackProgress 改用 renderTitleHeader ───────────────────


def test_a1_track_progress_uses_render_title_header():
    """A1：trackProgress 完成路徑用 renderTitleHeader(p) 重繪 multi-row 結構、
    不再用 textContent = el.textContent 清空結構。"""
    # 不應再有 current-title.textContent = el.textContent
    assert not re.search(
        r"getElementById\(['\"]current-title['\"]\)\.textContent\s*=\s*el\.textContent",
        STATIC_HTML,
    ), 'A1 殘留：current-title.textContent = el.textContent 必須改為 renderTitleHeader(p)'

    # 應有 const p = allPapers.find(p => p.id === paperId); + if (p) renderTitleHeader(p);
    assert re.search(
        r"const\s+p\s*=\s*allPapers\.find\(p\s*=>\s*p\.id\s*===\s*paperId\)",
        STATIC_HTML,
    ), 'A1：應有 const p = allPapers.find(p => p.id === paperId)'
    assert re.search(
        r"if\s*\(p\)\s*renderTitleHeader\(p\)",
        STATIC_HTML,
    ), 'A1：應有 if (p) renderTitleHeader(p) 重繪 multi-row 結構'


# ─────────────────── A2：empty-state 預設顯示反轉 ───────────────────


def test_a2_empty_state_default_visible_paper_content_hidden():
    """A2：HTML 內 #empty-state 預設顯示（無 style="display:none"）、
    #paper-content 預設 hide（style="display:none"）。"""
    # #empty-state 不應有 style="display:none"
    assert not re.search(
        r'id="empty-state"[^>]*style="display:none"',
        STATIC_HTML,
    ), 'A2：#empty-state 不應預設 display:none（loadPaper 內 toggle 改為顯式 show paper / hide empty）'

    # #paper-content 應有 style="display:none"
    assert re.search(
        r'id="paper-content"[^>]*style="display:none"',
        STATIC_HTML,
    ), 'A2：#paper-content 應預設 style="display:none"（初始無 paper 時不顯示）'


# ─────────────────── A3：customPrompt 新增 ───────────────────


def test_a3_prompt_modal_dom_exists():
    """A3.1：#prompt-modal DOM 結構存在、含 prompt-title / prompt-body / prompt-input /
    prompt-cancel / prompt-ok 子元素。"""
    # #prompt-modal modal-mask
    assert re.search(
        r'<div\s+id="prompt-modal"\s+class="modal-mask"',
        STATIC_HTML,
    ), 'A3.1：#prompt-modal modal-mask DOM 應存在'

    # 5 個子元素
    for elem_id in ('prompt-title', 'prompt-body', 'prompt-input', 'prompt-cancel', 'prompt-ok'):
        assert f'id="{elem_id}"' in STATIC_HTML, (
            f'A3.1：#prompt-modal 應含 id="{elem_id}" 子元素'
        )

    # prompt-input 套 .modal-input class（享受 BUG-F3 ship 的樣式）
    assert re.search(
        r'<input\s+type="text"\s+id="prompt-input"\s+class="modal-input"',
        STATIC_HTML,
    ), 'A3.1：#prompt-input 應 class="modal-input" 套用 BUG-F3 CSS'


def test_a3_custom_prompt_function_exposed():
    """A3.1：customPrompt 函式定義 + window.customPrompt 暴露 + Promise-based +
    validate hook + Enter 鍵送出。"""
    # function customPrompt 定義
    assert re.search(
        r'function\s+customPrompt\s*\(\s*\{[^}]*title\s*=\s*[\'"]輸入[\'"]',
        STATIC_HTML,
    ), 'A3.1：customPrompt 函式定義應存在、預設 title="輸入"'

    # Promise-based
    assert 'return new Promise(resolve =>' in STATIC_HTML, (
        'A3.1：customPrompt 應 Promise-based、回 Promise<string | null>'
    )

    # window.customPrompt 暴露
    assert 'window.customPrompt = customPrompt' in STATIC_HTML, (
        'A3.1：window.customPrompt 應對外暴露'
    )

    # validate hook + customAlert error display
    assert 'if (validate) {' in STATIC_HTML, 'A3.1：應有 validate hook'

    # Enter 鍵送出（input.onkeydown 內 e.key === 'Enter'）
    assert re.search(
        r"input\.onkeydown\s*=\s*\(e\)\s*=>\s*\{\s*if\s*\(e\.key\s*===\s*['\"]Enter['\"]\)\s*submit\(\)",
        STATIC_HTML,
    ), 'A3.1：Enter 鍵應觸發 submit()'


def test_a3_2_native_dialog_replaced():
    """A3.2：全檔不應再有 native alert/confirm/prompt 呼叫（排除 comment 與 hashtagAutocomplete 內部 confirm）。"""
    # 行級檢查、排除 // / /* */ / <!-- --> 與 hashtagAuto / function 定義
    def is_call_line(line):
        s = line.lstrip()
        if s.startswith('//') or s.startswith('*') or s.startswith('/*') or s.startswith('<!--'):
            return False
        return True

    # native alert(...) — 必含字串/變數參數、`alert(` 開頭非 customAlert
    bad_alert = []
    for i, line in enumerate(STATIC_HTML.split('\n'), 1):
        if not is_call_line(line):
            continue
        if re.search(r'(?<!custom)(?<![\w.])alert\s*\(', line):
            bad_alert.append(f'L{i}: {line.strip()[:80]}')
    assert not bad_alert, (
        f'A3.2：native alert(...) 殘留：\n' + '\n'.join(bad_alert)
    )

    # native confirm(...) — 排除 hashtagAutocomplete 內部 confirm() 方法呼叫 + function 定義
    bad_confirm = []
    for i, line in enumerate(STATIC_HTML.split('\n'), 1):
        if not is_call_line(line):
            continue
        # confirm( + 字面引號（不是內部 confirm() 無參數呼叫）
        if re.search(r"(?<!custom)(?<![\w.])confirm\s*\(\s*['\"`]", line):
            bad_confirm.append(f'L{i}: {line.strip()[:80]}')
    assert not bad_confirm, (
        f'A3.2：native confirm("...") 殘留：\n' + '\n'.join(bad_confirm)
    )

    # native prompt(...)
    bad_prompt = []
    for i, line in enumerate(STATIC_HTML.split('\n'), 1):
        if not is_call_line(line):
            continue
        if re.search(r"(?<!custom)(?<![\w.])prompt\s*\(\s*['\"`]", line):
            bad_prompt.append(f'L{i}: {line.strip()[:80]}')
    assert not bad_prompt, (
        f'A3.2：native prompt("...") 殘留：\n' + '\n'.join(bad_prompt)
    )


def test_a3_2_chat_input_focus_listener_removed():
    """A3.2：chat-input focus listener 應整段刪除（contenteditable=false 已防護、dead code）。"""
    # 不應再有 alert('請先選擇文件') 在 focus listener 內
    assert "alert('請先選擇文件')" not in STATIC_HTML, (
        'A3.2：focus listener 內 alert("請先選擇文件") 應整段刪除'
    )
    # 不應再有 chat-input addEventListener('focus', () => { ... if (!currentPaperId)
    assert not re.search(
        r"getElementById\(['\"]chat-input['\"]\)\.addEventListener\(['\"]focus['\"],\s*\(\s*\)\s*=>\s*\{[^}]*currentPaperId",
        STATIC_HTML,
    ), 'A3.2：chat-input focus listener 應整段刪除（contenteditable=false 已防護）'


# ─────────────────── A4：closeBizPopups 移除、統一 closePopups ───────────────────


def test_a4_close_biz_popups_removed():
    """A4：function closeBizPopups 定義應刪除、所有呼叫點改 closePopups。"""
    # function closeBizPopups 定義不應存在（只剩註解可包含字串）
    assert not re.search(
        r'^\s*function\s+closeBizPopups\s*\(',
        STATIC_HTML, re.MULTILINE,
    ), 'A4：function closeBizPopups 定義應刪除'

    # 呼叫點 closeBizPopups() 不應存在（只剩註解）
    # 注意：comments 含 "closeBizPopups" 字串但不是呼叫、排除 // 開頭行
    lines_with_call = [
        line for line in STATIC_HTML.split('\n')
        if 'closeBizPopups(' in line
        and not line.lstrip().startswith('//')
        and not line.lstrip().startswith('/*')
        and not line.lstrip().startswith('*')
        and 'BUG-F4 A4' not in line
    ]
    assert not lines_with_call, (
        f'A4：closeBizPopups() 呼叫應全改 closePopups()；殘留：{lines_with_call}'
    )


def test_a4_second_click_listener_removed():
    """A4：原 closeBizPopups 區塊的第二個 document click listener 應刪除、
    全檔只剩 prototype 區的 closePopups click listener（1 個）。"""
    # 找所有 document.addEventListener('click', ...) 註冊
    click_listeners = re.findall(
        r"document\.addEventListener\(['\"]click['\"]",
        STATIC_HTML,
    )
    # 應只剩 1 個（prototype L1539）；不可有 2 個（原 closeBizPopups 重複）
    assert len(click_listeners) == 1, (
        f'A4：document click listener 應只剩 1 個 (prototype closePopups)、'
        f'目前 {len(click_listeners)} 個；closeBizPopups 區塊的 listener 必須刪除'
    )


def test_a4_open_popup_uses_closePopups():
    """A4：openPopup（business 區）內呼叫改用 closePopups。"""
    # openPopup body 含 closePopups() 呼叫（取 function openPopup 之後 800 字）
    idx = STATIC_HTML.find('function openPopup(x, y, items)')
    assert idx > 0, 'A4：function openPopup 應存在'
    body = STATIC_HTML[idx:idx + 1200]
    # 開頭 closePopups()
    assert 'closePopups();' in body, 'A4：openPopup 開頭應 closePopups()（取代 closeBizPopups()）'
    # 按鈕 onclick 內 closePopups()
    assert re.search(
        r"ev\.stopPropagation\(\);\s*closePopups\(\);\s*it\.action\(\)",
        body,
    ), 'A4：openPopup 按鈕 onclick 應 ev.stopPropagation(); closePopups(); it.action()'

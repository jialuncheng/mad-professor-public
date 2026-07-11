"""RAG-1 Phase 2 P2-3：前端 chat hashtag token UI pytest（9 個、≥ 8）。

涵蓋 plan v2 §5.1 P2-3 行 + §3.3.5 四點防護 grep test：
- placeholder hint 含 hashtag（Q11 完整版）
- contenteditable div（非 textarea）+ data-placeholder + role
- :empty::before CSS placeholder（§3.3.5-#1）
- contenteditable="false" 視覺契約（§3.3.5-#2）
- 全域無殘留 textarea-only API（§3.3.5-#3）
- autocomplete dropdown 綁容器、bottom:100%（§3.3.5-#4）
- hashtag-token CSS class 存在
- components.md §11.2 Hashtag Token 章節存在
- 後端 /api/papers 回 user_tags（autocomplete 來源 Q9）
"""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STATIC_HTML = (ROOT / 'static' / 'index.html').read_text(encoding='utf-8')
COMPONENTS_MD = (ROOT / 'design' / 'docs' / 'components.md').read_text(encoding='utf-8')


# ─────────────────── 1. §3.3.1 placeholder hint（Q11 完整版）───────────────────


def test_chat_input_placeholder_contains_hashtag_hint():
    """chat-input 的 data-placeholder 含「# 可加入 hashtag 跨文獻搜尋」hint。"""
    # 至少 1 處 data-placeholder 含 hashtag 提示
    assert re.search(
        r'data-placeholder[^"]*"[^"]*#[^"]*hashtag[^"]*"',
        STATIC_HTML, re.IGNORECASE
    ), '#chat-input data-placeholder 應含 hashtag 提示'
    # 含完整版「跨文獻搜尋」字串（Q11）
    assert '跨文獻搜尋' in STATIC_HTML


# ─────────────────── 2. textarea → contenteditable div ───────────────────


def test_chat_input_is_contenteditable_div_not_textarea():
    """static/index.html 內 #chat-input 應為 contenteditable div、非 textarea。"""
    # 不應該再有 textarea id="chat-input"
    assert not re.search(
        r'<textarea\b[^>]*\bid=["\']chat-input["\']',
        STATIC_HTML
    ), 'chat-input 不應再是 textarea（P2-3 已改 contenteditable div）'
    # 應該有 div id="chat-input" + contenteditable
    assert re.search(
        r'<div\b[^>]*\bid=["\']chat-input["\'][^>]*\bcontenteditable=',
        STATIC_HTML
    ), 'chat-input 應為 <div id="chat-input" contenteditable=...>'
    # ARIA：role=textbox + aria-multiline
    assert re.search(r'role=["\']textbox["\']', STATIC_HTML)
    assert re.search(r'aria-multiline=["\']true["\']', STATIC_HTML)


# ─────────────────── 3. §3.3.5-#1 :empty::before CSS placeholder ───────────────────


def test_chat_input_has_empty_before_placeholder_css():
    """§3.3.5-#1：CSS `#chat-input:empty::before { content: attr(data-placeholder); ... }`。"""
    assert re.search(
        r'#chat-input:empty::before\s*\{[^}]*content:\s*attr\(data-placeholder\)',
        STATIC_HTML
    ), '應有 #chat-input:empty::before + content:attr(data-placeholder)'
    # pointer-events: none 防誤觸
    assert re.search(
        r'#chat-input:empty::before\s*\{[^}]*pointer-events:\s*none',
        STATIC_HTML, re.DOTALL
    )


# ─────────────────── 4. §3.3.5-#2 disabled 視覺契約 ───────────────────


def test_chat_input_disabled_visual_contract_via_contenteditable_false():
    """§3.3.5-#2：`#chat-input[contenteditable="false"]` 有顯式禁用樣式
    （`cursor: not-allowed` 等）對齊既有 textarea[disabled] UX。"""
    pat = re.compile(
        r'#chat-input\[contenteditable=["\']false["\']\]\s*\{[^}]*cursor:\s*not-allowed',
        re.DOTALL
    )
    assert pat.search(STATIC_HTML), (
        '#chat-input[contenteditable="false"] 應顯式設 cursor:not-allowed'
    )


# ─────────────────── 5. §3.3.5-#3 全域無殘留 textarea-only API ───────────────────


def test_chat_input_no_residual_textarea_value_refs():
    """§3.3.5-#3：static/index.html 內 chat-input 應已完成所有 textarea-only API 替換：
    - 不再 `getElementById('chat-input').disabled = ...` 直接寫屬性
    - 不再 `getElementById('chat-input').value`
    - 不再 `getElementById('chat-input').setAttribute('placeholder', ...)`（改 data-placeholder）
    - 不再 textarea autosize listener（ta.style.height = ...）
    """
    # 5a. .disabled = (true|false) 不應出現在 chat-input
    bad_disabled = re.findall(
        r"getElementById\(['\"]chat-input['\"]\)\.disabled\s*=",
        STATIC_HTML
    )
    assert not bad_disabled, (
        f'chat-input.disabled 應全部改 setAttribute("contenteditable", ...)；殘留 {len(bad_disabled)} 處'
    )

    # 5b. .value（屬性提取 / 賦值）不應出現在 chat-input 取得後的同行
    # 同行寫法：`document.getElementById('chat-input').value` 或 var = ... `input.value`
    # 全檔 grep `chat-input` 相關 .value
    bad_value = re.findall(
        r"getElementById\(['\"]chat-input['\"]\)\.value\b",
        STATIC_HTML
    )
    assert not bad_value, (
        f'chat-input.value 應改 .textContent.trim()；殘留 {len(bad_value)} 處'
    )

    # 5c. setAttribute('placeholder', ...) for chat-input 應改 data-placeholder
    bad_placeholder = re.findall(
        r"getElementById\(['\"]chat-input['\"]\)\.setAttribute\(\s*['\"]placeholder['\"]",
        STATIC_HTML
    )
    assert not bad_placeholder, (
        f'chat-input placeholder 屬性應改 data-placeholder；殘留 {len(bad_placeholder)} 處'
    )

    # 5d. textarea autosize（ta.style.height = ...）—— 全檔不應再有 ta.style.height
    bad_autosize = re.findall(r"\bta\.style\.height\s*=", STATIC_HTML)
    assert not bad_autosize, (
        f'textarea autosize listener 應移除（contenteditable 自然撐高）；殘留 {len(bad_autosize)} 處'
    )


# ─────────────────── 6. §3.3.5-#4 autocomplete dropdown 定位 ───────────────────


def test_hashtag_autocomplete_anchored_to_container():
    """§3.3.5-#4：#hashtag-autocomplete 用 position:absolute + bottom:100%
    + #chat-input-area 為 position:relative 錨點。"""
    assert re.search(
        r'#chat-input-area\s*\{[^}]*position:\s*relative',
        STATIC_HTML, re.DOTALL
    ), '#chat-input-area 應為 position:relative（dropdown 定位錨點）'
    assert re.search(
        r'#hashtag-autocomplete\.hashtag-popup\s*\{[^}]*position:\s*absolute',
        STATIC_HTML, re.DOTALL
    )
    assert re.search(
        r'#hashtag-autocomplete\.hashtag-popup\s*\{[^}]*bottom:\s*100%',
        STATIC_HTML, re.DOTALL
    ), 'dropdown 應 bottom:100%（永遠在 input 正上方）'


# ─────────────────── 7. hashtag-token CSS class 存在 ───────────────────


def test_hashtag_token_css_defined():
    """`.hashtag-token` + `.hashtag-token-remove` CSS 必須存在。"""
    assert re.search(r'\.hashtag-token\s*\{', STATIC_HTML), '.hashtag-token 樣式必須定義'
    assert re.search(r'\.hashtag-token-remove\s*\{', STATIC_HTML)
    # 藍色 = var(--color-accent)（依 components.md §11.2.2）
    pat = re.compile(
        r'\.hashtag-token\s*\{[^}]*background:\s*var\(--color-accent\)',
        re.DOTALL
    )
    assert pat.search(STATIC_HTML), '.hashtag-token 背景應為 var(--color-accent)'


# ─────────────────── 8. components.md §11.2 Hashtag Token ───────────────────


def test_components_md_has_section_11_2_hashtag_token():
    """design/docs/components.md 必須含 §11.2 Hashtag Token 章節（plan §3.3.3）。"""
    assert re.search(
        r'^##\s+11\.2\s+Hashtag\s+Token',
        COMPONENTS_MD, re.MULTILINE
    ), 'components.md 應含 `## 11.2 Hashtag Token` 章節'
    # 對齊 Tag Pill 區隔表（§11.2.5）
    assert '跟 §11 Tag Pill 的區別' in COMPONENTS_MD or '跟 §11' in COMPONENTS_MD
    # 必含 §3.3.5 防護段
    assert 'contenteditable' in COMPONENTS_MD


# ─────────────────── 9. 後端 /api/papers 回 user_tags（autocomplete Q9 來源）───────────────────


def test_api_papers_returns_user_tags():
    """Q9：autocomplete 來源 = allPapers user_tags 前端 cache。

    驗證兩條:
    1. 後端 paper_manager._to_dict 序列化 metadata（含 user_tags、Phase 1 R1 ship）
    2. 前端 collectAllUserTags 防禦既有 field shape inconsistency
       （Phase 1 既有：API 回 metadata、PATCH 後 local 寫 metadata_json）
    """
    pm_src = (ROOT / 'paper_manager.py').read_text(encoding='utf-8')
    # _to_dict 函式存在
    assert 'def _to_dict(' in pm_src, 'paper_manager._to_dict 應存在'
    # _to_dict 區塊（取下一個 def 之前的 60 行）含 'metadata' key 序列化
    idx = pm_src.find('def _to_dict(')
    block = pm_src[idx:idx + 2000]
    assert "'metadata'" in block or '"metadata"' in block, (
        '_to_dict 應在回傳 dict 中含 metadata key（含 user_tags、Phase 1 R1 ship）'
    )

    # 前端 collectAllUserTags 應讀 metadata 與 metadata_json 雙鍵
    assert 'p.metadata && p.metadata.user_tags' in STATIC_HTML, (
        'collectAllUserTags 應讀 p.metadata.user_tags（/api/papers 回傳 shape）'
    )
    assert 'p.metadata_json && p.metadata_json.user_tags' in STATIC_HTML, (
        'collectAllUserTags 應讀 p.metadata_json.user_tags（PATCH 後 local shape）'
    )

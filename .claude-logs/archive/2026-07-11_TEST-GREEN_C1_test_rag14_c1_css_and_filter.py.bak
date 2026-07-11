"""
RAG-14 C1 靜態驗收測試：CSS 氣泡滿寬 + sendMessage × 過濾
=============================================================
依 tasks_v1 §8 C1 Step 8 規格：
  - test_msg_user_has_sticky_positioning
  - test_msg_user_msg_ai_have_stretch_width
  - test_qa_group_css_block_exists
  - test_sendmessage_filters_hashtag_token_remove

所有測試為純靜態 grep，讀 static/index.html，無需 server 啟動。
"""

import pathlib
import re

STATIC_HTML = pathlib.Path(__file__).parent.parent / "static" / "index.html"


def _html() -> str:
    return STATIC_HTML.read_text(encoding="utf-8")


def test_msg_user_has_sticky_positioning():
    """
    .msg-user 必須有 position: sticky（C1 RAG-14 Sticky header 要求）。
    """
    content = _html()
    assert "position: sticky" in content, (
        ".msg-user block 缺少 'position: sticky'；請確認 C1 CSS 修改已落地。"
    )


def test_msg_user_msg_ai_have_stretch_width():
    """
    .msg-user 與 .msg-ai 皆須為 align-self: stretch（滿寬顯示）。
    count >= 2 確保兩個 block 都已改。
    """
    content = _html()
    count = content.count("align-self: stretch")
    assert count >= 2, (
        f"預期 'align-self: stretch' 出現 >= 2 次（.msg-user + .msg-ai），實際：{count}。"
        "請確認 C1 CSS 修改已落地。"
    )
    # 確認舊的 flex-end 與 flex-start 已移除
    assert "align-self: flex-end" not in content, (
        ".msg-user 仍含 'align-self: flex-end'，C1 修改未完整移除舊值。"
    )
    assert "align-self: flex-start" not in content, (
        ".msg-ai 仍含 'align-self: flex-start'，C1 修改未完整移除舊值。"
    )


def test_qa_group_css_block_exists():
    """
    .qa-group CSS block 必須存在（C2 DOM 結構前置，C1 一併加入 CSS）。
    """
    content = _html()
    assert ".qa-group" in content, (
        "找不到 '.qa-group' CSS 定義；請確認 C1 已在 .msg-user 後插入 .qa-group block。"
    )
    # 確認 gap: var(--space-4) 存在於 qa-group 區塊附近
    # 以正規表示式抓取 .qa-group { ... } 區塊
    match = re.search(r"\.qa-group\s*\{([^}]+)\}", content)
    assert match is not None, ".qa-group {} 區塊未找到（格式可能異常）。"
    block = match.group(1)
    assert "var(--space-4)" in block, (
        f".qa-group block 缺少 'gap: var(--space-4)'；block 內容：{block.strip()}"
    )


def test_sendmessage_filters_hashtag_token_remove():
    """
    sendMessage 必須用 cloneNode(true) + querySelectorAll('.hashtag-token-remove')
    過濾 × 按鈕，避免 '×' 字元混入送出的 query（C1 RAG-14 × 過濾要求）。
    """
    content = _html()
    assert "cloneNode(true)" in content, (
        "sendMessage 缺少 'cloneNode(true)'；"
        "請確認 C1 已改為 clone node 模式提取 query。"
    )
    assert "querySelectorAll('.hashtag-token-remove')" in content, (
        "sendMessage 缺少 \"querySelectorAll('.hashtag-token-remove')\"；"
        "請確認 C1 已加入 × 按鈕過濾邏輯。"
    )

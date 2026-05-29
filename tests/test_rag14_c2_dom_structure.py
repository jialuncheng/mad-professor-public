"""
RAG-14 C2 靜態驗收測試：loadChatHistory QA-group DOM + in_progress + sendMessage 包裝
=======================================================================================
依 tasks_v1 §8 C2 Step 5 規格：
  - test_loadchathistory_uses_currentgroup_for_qa_group
  - test_inprogress_reuses_currentgroup
  - test_sendmessage_wraps_in_qa_group

所有測試為純靜態 grep，讀 static/index.html，無需 server 啟動。
"""

import pathlib

STATIC_HTML = pathlib.Path(__file__).parent.parent / "static" / "index.html"


def _html() -> str:
    return STATIC_HTML.read_text(encoding="utf-8")


def test_loadchathistory_uses_currentgroup_for_qa_group():
    """
    loadChatHistory 的 history.forEach 必須使用 currentGroup 包裝每個 Q&A 組合：
    - 宣告 `let currentGroup = null`
    - 建立 `.qa-group` div 並指派給 currentGroup（C2 RAG-14）
    """
    content = _html()
    assert "let currentGroup = null" in content, (
        "loadChatHistory 缺少 'let currentGroup = null'；"
        "請確認 C2 已在 history.forEach 前宣告 currentGroup。"
    )
    assert "currentGroup = document.createElement('div')" in content, (
        "loadChatHistory 缺少 \"currentGroup = document.createElement('div')\"；"
        "請確認 C2 在 msg.role === 'user' 時建立新的 qa-group 容器。"
    )
    assert "currentGroup.className = 'qa-group'" in content, (
        "loadChatHistory 缺少 \"currentGroup.className = 'qa-group'\"；"
        "請確認 C2 正確設定 qa-group class。"
    )


def test_inprogress_reuses_currentgroup():
    """
    loadChatHistory 的 in_progress 區塊必須將 aiMsg append 到 currentGroup，
    而非直接 append 到 messages（C2 RAG-14 in_progress currentGroup 沿用）。
    """
    content = _html()
    assert "currentGroup.appendChild(aiMsg)" in content, (
        "找不到 'currentGroup.appendChild(aiMsg)'；"
        "請確認 C2 in_progress 區塊已改為沿用 currentGroup 而非直接 messages.appendChild。"
    )
    # 確認 in_progress 仍有 fallback（防禦性）
    assert "messages.appendChild(aiMsg)" in content, (
        "in_progress 缺少 fallback 的 'messages.appendChild(aiMsg)'；"
        "請確認 C2 在 currentGroup 為 null 時有 else fallback。"
    )


def test_sendmessage_wraps_in_qa_group():
    """
    sendMessage 必須建立 qaGroup (.qa-group) 容器，
    並將 userMsg 與 aiMsg 皆 appendChild 到 qaGroup（C2 RAG-14）。
    """
    content = _html()
    assert "qaGroup.className = 'qa-group'" in content, (
        "sendMessage 缺少 \"qaGroup.className = 'qa-group'\"；"
        "請確認 C2 已在 sendMessage 建立 qaGroup 容器。"
    )
    assert "qaGroup.appendChild(userMsg)" in content, (
        "sendMessage 缺少 'qaGroup.appendChild(userMsg)'；"
        "請確認 C2 userMsg 已改掛到 qaGroup 而非直接 messages。"
    )
    assert "qaGroup.appendChild(aiMsg)" in content, (
        "sendMessage 缺少 'qaGroup.appendChild(aiMsg)'；"
        "請確認 C2 aiMsg 已改掛到 qaGroup 而非直接 messages。"
    )

"""
RAG-13-HOTFIX-1：scroll 捕獲誤傷防禦測試

修復：window scroll 捕獲監聽器在彈出選單（.ctx-popup）內部滾動時，
誤呼叫 closePopups() 導致選單消失的 Regression Bug。
"""

import re
from pathlib import Path

STATIC_HTML = Path(__file__).parent.parent / "static" / "index.html"
STATIC_HTML = STATIC_HTML.read_text(encoding="utf-8")


def test_scroll_intercept_old_bare_callback_removed():
    """RAG-13-HOTFIX-1：舊的裸回調 closePopups, true 應已替換（不應存在）。"""
    # 確認舊寫法「window.addEventListener('scroll', closePopups, true)」已不存在
    assert "addEventListener('scroll', closePopups, true)" not in STATIC_HTML, (
        "RAG-13-HOTFIX-1：舊的裸 closePopups 捕獲監聽器應已替換為帶 ctx-popup 過濾的箭頭函式；"
        "目前仍存在舊寫法，表示修復未生效"
    )


def test_scroll_intercept_ctx_popup_guard_exists():
    """RAG-13-HOTFIX-1：新的 ctx-popup guard 字串應存在於 scroll 監聽器中。"""
    # 確認新的 guard 語法存在
    assert "e.target.closest('.ctx-popup')" in STATIC_HTML, (
        "RAG-13-HOTFIX-1：scroll 監聽器應包含 e.target.closest('.ctx-popup') guard，"
        "防止彈出選單內部滾動誤觸 closePopups()；目前字串不存在"
    )

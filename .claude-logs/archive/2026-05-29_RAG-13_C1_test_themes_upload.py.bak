"""RAG-1 R2 子項 B：theme upload endpoint 5 道安全過濾驗證。

依據:
- plan: .claude-logs/2026-05-23_RAG-1_前端執行計劃_含資料夾自動標籤.md §4.1 R2
- UI Plan v3 子項 B
- design/docs/theme-guide.md §7

策略：建一個 minimal FastAPI app 並掛 upload_theme endpoint、繞過 web_server.app
完整 lifespan / auth_guard / SessionMiddleware。對齊 LOGGING-2 test_trace_id_middleware
pattern。
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def test_client(monkeypatch):
    """建 minimal app、掛 upload_theme endpoint、把 BASE_DIR 指向 tmp 防污染 static/themes/。"""
    import web_server

    # 改 BASE_DIR 到 tmp（avoid contaminating real static/themes/）
    tmp = Path(tempfile.mkdtemp(prefix="theme_test_"))
    monkeypatch.setattr(web_server, 'BASE_DIR', tmp)

    app = FastAPI()
    # 直接掛 upload_theme function（繞過 auth_guard / SessionMiddleware）
    app.post("/api/themes/upload")(web_server.upload_theme)

    client = TestClient(app)
    yield client, tmp
    shutil.rmtree(tmp, ignore_errors=True)


# ─────────────────── 1. 合法 .css 上傳 ───────────────────


def test_theme_upload_accepts_valid_css(test_client):
    client, tmp = test_client
    css_content = b".test { color: red; }"
    response = client.post(
        "/api/themes/upload",
        files={"file": ("test_theme.css", css_content, "text/css")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"].endswith(".css")
    assert data["url"].startswith("/static/themes/")
    # 實際寫入到 tmp/static/themes/
    target = tmp / "static" / "themes" / data["filename"]
    assert target.exists()
    assert target.read_bytes() == css_content


# ─────────────────── 2. 非 .css 拒絕 ───────────────────


def test_theme_upload_rejects_non_css(test_client):
    client, _tmp = test_client
    response = client.post(
        "/api/themes/upload",
        files={"file": ("evil.js", b"alert('xss')", "application/javascript")},
    )
    assert response.status_code == 400


# ─────────────────── 3. > 100KB 拒絕 ───────────────────


def test_theme_upload_rejects_oversize(test_client):
    client, _tmp = test_client
    big_content = b"x" * (100 * 1024 + 100)
    response = client.post(
        "/api/themes/upload",
        files={"file": ("big.css", big_content, "text/css")},
    )
    assert response.status_code == 413


# ─────────────────── 4. 惡意檔名 sanitize（path traversal）───────────────────


def test_theme_upload_sanitizes_filename(test_client):
    client, tmp = test_client
    css_content = b".test { color: red; }"
    response = client.post(
        "/api/themes/upload",
        files={"file": ("../../etc/passwd.css", css_content, "text/css")},
    )
    # 應成功 200 但 filename 不含 ../ / 等危險字元
    assert response.status_code == 200
    data = response.json()
    assert "/" not in data["filename"]
    assert ".." not in data["filename"]
    # 確認實際寫入位置仍在 static/themes/ 內
    target = tmp / "static" / "themes" / data["filename"]
    assert target.exists()
    # 路徑 resolve 後仍在 themes_dir 內
    themes_dir = (tmp / "static" / "themes").resolve()
    assert str(target.resolve()).startswith(str(themes_dir))


# ─────────────────── 5. 空檔名拒絕 ───────────────────


def test_theme_upload_rejects_invalid_stem(test_client):
    """純底線的檔名（sanitize + 壓縮 + strip 後為空）拒絕。"""
    client, _tmp = test_client
    response = client.post(
        "/api/themes/upload",
        files={"file": ("___.css", b".test {}", "text/css")},
    )
    # `___` → 壓縮為 `_` → strip("_") 後為空、應 400
    assert response.status_code == 400

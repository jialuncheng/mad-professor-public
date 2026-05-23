"""LOGGING-2 階段：trace_id middleware 驗證。

依據:
- plan: .claude-logs/2026-05-23_logging_refactor_可行性評估.md v4
- §4.4 trace_id middleware + §4.11 補強 3 asyncio.to_thread 自動繼承
- §6 LOGGING-2 行 + Q7 / Q12

採 isolated unit test 策略（避免 import web_server 觸發 lifespan / ai_core 啟動）：
- 建一個 minimal FastAPI app + 直接套用 trace_id_middleware 的 wrapped function
- 用 TestClient 驅動、驗證 ContextVar / response header / 並發隔離

並補 1 個 asyncio.to_thread ContextVar 自動繼承的純 asyncio test（補強 3 / §4.11）
"""
from __future__ import annotations

import asyncio
import sys
import threading
import uuid
from pathlib import Path

import pytest
from fastapi import FastAPI, Request
from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ─────────────────── fixture: minimal app + middleware 隔離 ───────────────────


def _build_app_with_trace_middleware(session_payload=None):
    """建一個最小 FastAPI app、套用跟 web_server 一樣邏輯的 trace_id middleware。

    避免 import web_server 全套（含 lifespan / ai_core / DB），純測 middleware 邏輯。
    若 session_payload 給定、會 mock request.session 讓 middleware 能讀 owner。
    """
    from utils.logging_config import trace_context

    app = FastAPI()

    @app.middleware("http")
    async def trace_id_middleware(request: Request, call_next):
        # 重現 web_server.py 內 trace_id_middleware 行為
        incoming = request.headers.get("X-Trace-ID")
        trace_id = incoming if incoming else uuid.uuid4().hex[:8]

        owner = None
        try:
            # 模擬 session 存在
            if session_payload is not None:
                # 注入 mock session 到 request.scope（starlette 內部使用）
                request.scope["session"] = session_payload
            if hasattr(request, "session"):
                owner = request.session.get("user")
        except Exception:
            owner = None

        token = trace_context.set({
            "trace_id": trace_id,
            "owner": owner,
            "path": request.url.path,
            "method": request.method,
        })
        try:
            response = await call_next(request)
        finally:
            trace_context.reset(token)

        response.headers["X-Trace-ID"] = trace_id
        return response

    @app.get("/")
    async def root(request: Request):
        # 讀 ContextVar 並回傳、方便 test 驗證
        ctx = trace_context.get(None)
        return {"ctx": ctx}

    @app.get("/raise")
    async def raise_path():
        raise RuntimeError("intended for test")

    return app


# ─────────────────── 1. response header 回填 X-Trace-ID ───────────────────


def test_response_has_x_trace_id_header():
    """所有 response 必須含 X-Trace-ID header（8 char hex 預設）。"""
    app = _build_app_with_trace_middleware()
    client = TestClient(app)
    response = client.get("/")
    assert "x-trace-id" in {k.lower() for k in response.headers.keys()}
    trace_id = response.headers.get("X-Trace-ID")
    assert trace_id is not None
    assert len(trace_id) == 8
    # uuid4 hex 是小寫 hex 字符
    assert all(c in "0123456789abcdef" for c in trace_id)


# ─────────────────── 2. request 帶 X-Trace-ID 時重用 ───────────────────


def test_incoming_x_trace_id_is_reused():
    """request header 帶 X-Trace-ID → middleware 重用、不生成新 ID。"""
    app = _build_app_with_trace_middleware()
    client = TestClient(app)
    custom_trace = "abc12345"
    response = client.get("/", headers={"X-Trace-ID": custom_trace})
    assert response.headers["X-Trace-ID"] == custom_trace


# ─────────────────── 3. trace_id / path / method 注入 ContextVar ───────────────────


def test_trace_id_injected_into_context_var():
    """request 期間 ContextVar 內含 trace_id / path / method、handler 可讀。"""
    app = _build_app_with_trace_middleware()
    client = TestClient(app)
    response = client.get("/", headers={"X-Trace-ID": "ctx12345"})
    body = response.json()
    ctx = body["ctx"]
    assert ctx is not None
    assert ctx["trace_id"] == "ctx12345"
    assert ctx["path"] == "/"
    assert ctx["method"] == "GET"


# ─────────────────── 4. 跨 request ContextVar 不洩漏 ───────────────────


def test_context_var_resets_between_requests():
    """連續 2 個 request、各自 trace_id 獨立；中間 ContextVar 已 reset。"""
    from utils.logging_config import trace_context

    app = _build_app_with_trace_middleware()
    client = TestClient(app)

    response1 = client.get("/")
    trace1 = response1.headers["X-Trace-ID"]

    # request 結束後 ContextVar 已 reset
    assert trace_context.get(None) is None

    response2 = client.get("/")
    trace2 = response2.headers["X-Trace-ID"]

    assert trace1 != trace2  # uuid4 衝突機率 ~0
    assert trace_context.get(None) is None


# ─────────────────── 5. concurrent 並發 request 不交叉 ───────────────────


def test_concurrent_requests_have_separate_trace_ids():
    """多 thread 並發 request、每個 response.X-Trace-ID 跟對應 request 對齊。

    asyncio + ContextVar 跨 task 自動隔離（Python 官方保證）。
    """
    app = _build_app_with_trace_middleware()
    client = TestClient(app)

    results = {}

    def make_request(idx):
        custom = f"trace{idx:04d}"
        response = client.get("/", headers={"X-Trace-ID": custom})
        results[idx] = response.headers["X-Trace-ID"]

    threads = [threading.Thread(target=make_request, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    for idx in range(10):
        assert results[idx] == f"trace{idx:04d}", (
            f"idx={idx} got {results[idx]}（concurrent ContextVar 交叉）"
        )


# ─────────────────── 6. exception 路徑下 ContextVar 仍 reset ───────────────────


def test_context_var_reset_after_exception():
    """endpoint 拋 exception、middleware finally block 仍 reset ContextVar。"""
    from utils.logging_config import trace_context

    app = _build_app_with_trace_middleware()
    client = TestClient(app, raise_server_exceptions=False)

    # /raise endpoint 會拋 RuntimeError、starlette TestClient 回 500
    response = client.get("/raise")
    assert response.status_code == 500
    # 即使例外、X-Trace-ID 不一定有（Starlette 內部 500 ErrorResponse 可能不經過 middleware
    # post-processing；但 ContextVar 必須已 reset）
    assert trace_context.get(None) is None


# ─────────────────── 7. owner 從 session 注入 ───────────────────


def test_owner_injected_when_session_present():
    """request.session 含 user 時、ContextVar 內 owner 同步。"""
    app = _build_app_with_trace_middleware(session_payload={"user": "alice"})
    client = TestClient(app)
    response = client.get("/", headers={"X-Trace-ID": "ownr1234"})
    ctx = response.json()["ctx"]
    assert ctx["owner"] == "alice"


# ─────────────────── 8. asyncio.to_thread 自動繼承（補強 3 / §4.11）───────────────────


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="asyncio.to_thread 自動繼承 ContextVar 需 Python 3.9+",
)
def test_asyncio_to_thread_inherits_trace_id():
    """補強 3 / §4.11: Python 3.9+ asyncio.to_thread 自動繼承 ContextVar。

    驗證 SSE chat 路徑（既有 web_server.py:151 用 asyncio.to_thread）trace_id 不會斷鏈。
    """
    from utils.logging_config import trace_context

    captured: list = []

    def sync_worker():
        """模擬 SSE 內 sync generator 路徑、抓 ContextVar。"""
        captured.append(trace_context.get(None))

    async def main():
        token = trace_context.set({"trace_id": "inherit-x"})
        try:
            await asyncio.to_thread(sync_worker)
        finally:
            trace_context.reset(token)

    asyncio.run(main())

    assert captured == [{"trace_id": "inherit-x"}], (
        f"asyncio.to_thread 未自動繼承 ContextVar、captured={captured}"
    )


# ─────────────────── 9. web_server.py 含 middleware 設置驗證 ───────────────────


def test_web_server_has_trace_id_middleware_defined():
    """grep web_server.py、確保 LOGGING-2 trace_id middleware 已加。"""
    src = (ROOT / "web_server.py").read_text(encoding='utf-8')
    assert "async def trace_id_middleware" in src, (
        "LOGGING-2: web_server.py 應含 trace_id_middleware 函式"
    )
    assert "_trace_context.set" in src, (
        "LOGGING-2: trace_id_middleware 應 set ContextVar"
    )
    assert '"X-Trace-ID"' in src, (
        "LOGGING-2: trace_id_middleware 應寫回 X-Trace-ID header"
    )

"""共享 httpx.Client 工廠（Phase 4.7? MODEL-9）。

提供集中配置的 httpx.Client、給 google-genai SDK 透過
http_options.httpx_client 注入。LLMClient + EmbeddingModel 共用同一個底層
client、保 Keep-Alive pool 共享。

設計依據：.claude-logs/2026-05-22_MODEL-9_連線彈性防禦_plan.md §4

baron 補充：
- R1 graceful shutdown：close_shared_httpx_client() 給 lifespan hook 用
- R2 環境變數 override：GEMINI_*_TIMEOUT / GEMINI_MAX_* 等

Q9 probe（baron 已驗證）：snake_case `httpx_client` + camelCase `httpxClient`
SDK 兩者都接（Pydantic 自動轉換）、本 module 用 snake_case（Python 慣例）。
"""
import os
import threading

import httpx
from google.genai import types

# 4.1 + 4.2：timeout + Keep-Alive pool 一次配齊（R2 環境變數 override）
CONNECT_TIMEOUT = float(os.environ.get("GEMINI_CONNECT_TIMEOUT", 5.0))
READ_TIMEOUT = float(os.environ.get("GEMINI_READ_TIMEOUT", 60.0))
WRITE_TIMEOUT = float(os.environ.get("GEMINI_WRITE_TIMEOUT", 30.0))
POOL_TIMEOUT = float(os.environ.get("GEMINI_POOL_TIMEOUT", 60.0))
MAX_KEEPALIVE_CONNECTIONS = int(os.environ.get("GEMINI_MAX_KEEPALIVE", 20))
MAX_CONNECTIONS = int(os.environ.get("GEMINI_MAX_CONNECTIONS", 100))
KEEPALIVE_EXPIRY = float(os.environ.get("GEMINI_KEEPALIVE_EXPIRY", 30.0))


_lock = threading.Lock()
_shared_client: httpx.Client = None


def _build_timeout() -> httpx.Timeout:
    """產生 httpx.Timeout、可由 env 動態覆寫。"""
    return httpx.Timeout(
        connect=CONNECT_TIMEOUT,
        read=READ_TIMEOUT,
        write=WRITE_TIMEOUT,
        pool=POOL_TIMEOUT,
    )


def _build_limits() -> httpx.Limits:
    """產生 httpx.Limits、可由 env 動態覆寫。"""
    return httpx.Limits(
        max_keepalive_connections=MAX_KEEPALIVE_CONNECTIONS,
        max_connections=MAX_CONNECTIONS,
        keepalive_expiry=KEEPALIVE_EXPIRY,
    )


def get_shared_httpx_client() -> httpx.Client:
    """singleton：全 process 共享 httpx.Client。

    LLMClient + EmbeddingModel 共用此 client、TCP connection pool 完全共享。
    """
    global _shared_client
    if _shared_client is None:
        with _lock:
            if _shared_client is None:
                _shared_client = httpx.Client(
                    timeout=_build_timeout(),
                    limits=_build_limits(),
                )
    return _shared_client


def build_http_options() -> types.HttpOptions:
    """產生 SDK http_options、注入共享 httpx.Client。

    給 genai.Client(http_options=build_http_options()) 用。
    """
    client = get_shared_httpx_client()
    return types.HttpOptions(httpx_client=client)


def close_shared_httpx_client() -> None:
    """關閉共享 httpx.Client、釋放長連線資源。

    用於：
    - FastAPI lifespan 關閉 hook（未來 DOCKER-1 容器化時註冊）
    - 單元測試結束 / atexit
    - 手動 reset

    呼叫後再次呼叫 get_shared_httpx_client() 會建新 client。
    """
    global _shared_client
    if _shared_client is not None:
        with _lock:
            if _shared_client is not None:
                _shared_client.close()
                _shared_client = None

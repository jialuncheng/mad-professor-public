"""Phase 4.7? MODEL-9: llm/_http_client.py 工廠驗證。

驗證：
- 共享 singleton（同一 process 同一 client）
- timeout / limits 配置正確（plan §4.1）
- build_http_options 注入到 SDK
- close_shared_httpx_client 釋放並可重建（baron R1）
- 環境變數 override 生效（baron R2）
"""
import importlib
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _purge_http_client_module():
    """強制 fully purge llm._http_client from caches、讓重新 import 觸發 module-level env 讀取。"""
    sys.modules.pop("llm._http_client", None)
    # 也要從 llm 套件 namespace 拔掉、否則 `from llm import _http_client` 還是回舊 module
    llm_pkg = sys.modules.get("llm")
    if llm_pkg is not None and hasattr(llm_pkg, "_http_client"):
        delattr(llm_pkg, "_http_client")


@pytest.fixture(autouse=True)
def reset_module():
    """每個 test 前 reset module-level singleton + env、避免污染。"""
    # 清除 env override
    for key in [
        "GEMINI_CONNECT_TIMEOUT", "GEMINI_READ_TIMEOUT",
        "GEMINI_WRITE_TIMEOUT", "GEMINI_POOL_TIMEOUT",
        "GEMINI_MAX_KEEPALIVE", "GEMINI_MAX_CONNECTIONS",
        "GEMINI_KEEPALIVE_EXPIRY",
    ]:
        os.environ.pop(key, None)
    _purge_http_client_module()
    yield
    # cleanup: 關閉 singleton
    if "llm._http_client" in sys.modules:
        from llm._http_client import close_shared_httpx_client
        close_shared_httpx_client()
    _purge_http_client_module()


def test_shared_client_singleton():
    """get_shared_httpx_client() 多次呼叫回同一 instance。"""
    from llm._http_client import get_shared_httpx_client
    c1 = get_shared_httpx_client()
    c2 = get_shared_httpx_client()
    assert c1 is c2, "singleton 不工作：兩次 get 回不同 instance"


def test_shared_client_default_timeout():
    """預設 timeout 配置：connect=5 / read=60 / write=30 / pool=60。"""
    from llm._http_client import get_shared_httpx_client
    client = get_shared_httpx_client()
    timeout = client.timeout
    assert timeout.connect == 5.0, f"connect={timeout.connect}"
    assert timeout.read == 60.0, f"read={timeout.read}"
    assert timeout.write == 30.0, f"write={timeout.write}"
    assert timeout.pool == 60.0, f"pool={timeout.pool}"


def test_env_override_read_timeout():
    """R2: GEMINI_READ_TIMEOUT 環境變數可 override 預設值。"""
    os.environ["GEMINI_READ_TIMEOUT"] = "120.0"
    _purge_http_client_module()
    from llm import _http_client as mod
    client = mod.get_shared_httpx_client()
    assert client.timeout.read == 120.0, f"env override 失敗: read={client.timeout.read}"


def test_env_override_multiple_values():
    """R2: 多個 env 變數同時 override。"""
    os.environ["GEMINI_CONNECT_TIMEOUT"] = "10.0"
    os.environ["GEMINI_MAX_KEEPALIVE"] = "50"
    os.environ["GEMINI_KEEPALIVE_EXPIRY"] = "60.0"
    _purge_http_client_module()
    from llm import _http_client as mod
    assert mod.CONNECT_TIMEOUT == 10.0
    assert mod.MAX_KEEPALIVE_CONNECTIONS == 50
    assert mod.KEEPALIVE_EXPIRY == 60.0


def test_build_http_options_returns_HttpOptions():
    """build_http_options() 回 types.HttpOptions、含 httpx_client。"""
    from google.genai import types
    from llm._http_client import build_http_options, get_shared_httpx_client
    opts = build_http_options()
    assert isinstance(opts, types.HttpOptions)
    # SDK Pydantic model 兩種命名都接（snake_case / camelCase）
    shared = get_shared_httpx_client()
    # 驗證 httpx_client 屬性可取到、且指向共享 client
    client_attr = getattr(opts, 'httpx_client', None) or getattr(opts, 'httpxClient', None)
    assert client_attr is shared, "HttpOptions.httpx_client 未指向共享 client"


def test_close_shared_client_releases_and_rebuild():
    """R1: close_shared_httpx_client() 關閉並可重新 get 建新 instance。"""
    from llm._http_client import (
        get_shared_httpx_client,
        close_shared_httpx_client,
    )
    c1 = get_shared_httpx_client()
    assert not c1.is_closed, "新建 client 不該已關閉"
    close_shared_httpx_client()
    assert c1.is_closed, "close 後原 client 應該已關閉"
    # 再次 get 應該得到新 instance
    c2 = get_shared_httpx_client()
    assert c2 is not c1, "close 後新 get 應該是新 instance"
    assert not c2.is_closed


def test_limits_default_config():
    """預設 limits 配置：max_keepalive=20 / max_connections=100 / keepalive_expiry=30。"""
    from llm._http_client import (
        MAX_KEEPALIVE_CONNECTIONS, MAX_CONNECTIONS, KEEPALIVE_EXPIRY,
    )
    assert MAX_KEEPALIVE_CONNECTIONS == 20
    assert MAX_CONNECTIONS == 100
    assert KEEPALIVE_EXPIRY == 30.0

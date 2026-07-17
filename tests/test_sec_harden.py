"""SEC-HARDEN 後端安全縱深加固守衛測試。

C1 — Login Hardening（登入加固）：
  #3 XFF 可信代理閘控（右向左解析）：_resolve_client_ip
     - peer 非可信 → 偽造 X-Forwarded-For 不影響 rate-limit key（恆用 socket peer）
     - peer 可信 → 由右向左剝除可信代理、取第一個非白名單 IP（嚴禁最左值）
  #8 login timing 等化：錯誤帳號 / AUTH_PASSWORD_HASH 未設 → 亦跑一次 dummy
     bcrypt 比對（模組級常數 _DUMMY_BCRYPT_HASH）；認證結果判定不變。

C2 — CORS Restriction（CORS 收斂）：
  #4 CORSMiddleware allow_origins 由 ["*"] 收斂為 settings.CORS_ALLOW_ORIGINS
     顯式白名單（env 覆寫、"*" 於 settings 層一律剔除）；不啟用 allow_credentials。

（C3 例外遮蔽 / C4 主題守衛 之測試於各自 commit 逐階段追加。）
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import bcrypt
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import settings  # noqa: E402
# 注意：import web_server 會 register routes + 建 FastAPI app（無副作用、
# lifespan 不會跑除非 server start）。我們只用 _resolve_client_ip / login handler。
import web_server  # noqa: E402


def _fake_request(peer: str, xff: str | None = None):
    """最小 Request 替身：僅 _resolve_client_ip 消費之 client.host + headers。"""
    headers = {}
    if xff is not None:
        headers["X-Forwarded-For"] = xff
    return SimpleNamespace(
        client=SimpleNamespace(host=peer),
        headers=headers,
    )


# ── #3 XFF 可信代理閘控 ──────────────────────────────────────────────


class TestResolveClientIp:
    def test_untrusted_peer_ignores_forged_xff(self, monkeypatch):
        """peer 非可信 → 偽造 XFF 完全不採信、key 恆為 socket peer。"""
        monkeypatch.setattr(settings, "TRUSTED_PROXIES", frozenset())
        req = _fake_request("203.0.113.7", xff="1.2.3.4")
        assert web_server._resolve_client_ip(req) == "203.0.113.7"

    def test_untrusted_peer_forged_xff_rotation_same_key(self, monkeypatch):
        """攻擊者每次換偽造 XFF、key 仍收斂同一 socket peer（鎖定可觸發）。"""
        monkeypatch.setattr(settings, "TRUSTED_PROXIES", frozenset())
        keys = {
            web_server._resolve_client_ip(_fake_request("203.0.113.7", xff=f"10.9.8.{i}"))
            for i in range(5)
        }
        assert keys == {"203.0.113.7"}

    def test_trusted_peer_right_to_left_skips_forged_leftmost(self, monkeypatch):
        """peer 可信 → 右向左剝可信代理；最左偽造值不得被採信。

        鏈 `fake, real, proxy`（proxy ∈ 白名單）→ 應取 real、非最左 fake。
        """
        monkeypatch.setattr(settings, "TRUSTED_PROXIES", frozenset({"10.0.0.1"}))
        req = _fake_request("10.0.0.1", xff="6.6.6.6, 198.51.100.23, 10.0.0.1")
        assert web_server._resolve_client_ip(req) == "198.51.100.23"

    def test_trusted_peer_simple_chain(self, monkeypatch):
        """peer 可信 + 單值 XFF → 取該真實 client IP（依 XFF 分桶）。"""
        monkeypatch.setattr(settings, "TRUSTED_PROXIES", frozenset({"10.0.0.1"}))
        req = _fake_request("10.0.0.1", xff="198.51.100.23")
        assert web_server._resolve_client_ip(req) == "198.51.100.23"

    def test_trusted_peer_multi_trusted_hops(self, monkeypatch):
        """多層可信代理全剝除、取第一個非白名單 IP。"""
        monkeypatch.setattr(
            settings, "TRUSTED_PROXIES", frozenset({"10.0.0.1", "10.0.0.2"})
        )
        req = _fake_request("10.0.0.1", xff="198.51.100.23, 10.0.0.2, 10.0.0.1")
        assert web_server._resolve_client_ip(req) == "198.51.100.23"

    def test_trusted_peer_empty_or_all_trusted_falls_back_to_peer(self, monkeypatch):
        """XFF 缺失 / 鏈全屬可信代理 → 回退 socket peer（不崩潰、不採空值）。"""
        monkeypatch.setattr(settings, "TRUSTED_PROXIES", frozenset({"10.0.0.1"}))
        assert web_server._resolve_client_ip(_fake_request("10.0.0.1")) == "10.0.0.1"
        req = _fake_request("10.0.0.1", xff="10.0.0.1, 10.0.0.1")
        assert web_server._resolve_client_ip(req) == "10.0.0.1"

    def test_no_client_returns_unknown(self, monkeypatch):
        """request.client 缺失（測試 client 場景）→ 'unknown' 降級不炸。"""
        monkeypatch.setattr(settings, "TRUSTED_PROXIES", frozenset())
        req = SimpleNamespace(client=None, headers={})
        assert web_server._resolve_client_ip(req) == "unknown"

    def test_leftmost_take_removed_from_source(self):
        """源碼守衛：login 區不得殘留 XFF 最左值取法 split(",")[0]。"""
        src = (ROOT / "web_server.py").read_text(encoding="utf-8")
        assert 'split(",")[0]' not in src


# ── #8 login timing 等化（dummy bcrypt）─────────────────────────────


@pytest.fixture()
def login_env(monkeypatch):
    """隔離 login 全域狀態 + 固定認證 config（正確帳號 admin / 已設 hash）。"""
    real_hash = bcrypt.hashpw(b"correct-password", bcrypt.gensalt(rounds=4)).decode()
    monkeypatch.setattr(settings, "AUTH_USERNAME", "admin")
    monkeypatch.setattr(settings, "AUTH_PASSWORD_HASH", real_hash)
    monkeypatch.setattr(settings, "TRUSTED_PROXIES", frozenset())
    monkeypatch.setattr(web_server, "_login_attempts", {})
    yield real_hash


def _post_login(client, username: str, password: str):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


class TestLoginTimingEqualization:
    def test_dummy_hash_is_valid_bcrypt(self):
        """模組級 dummy 常數必須為合法 bcrypt hash（checkpw 可跑、不拋例外）。"""
        assert not bcrypt.checkpw(
            b"any-password", web_server._DUMMY_BCRYPT_HASH.encode("utf-8")
        )

    def test_wrong_username_runs_dummy_bcrypt(self, login_env, monkeypatch):
        """錯誤帳號路徑必須跑一次 bcrypt 比對（對 dummy hash）。"""
        from fastapi.testclient import TestClient

        calls = []
        orig = bcrypt.checkpw

        def spy(pw, hashed):
            calls.append(hashed)
            return orig(pw, hashed)

        monkeypatch.setattr(web_server.bcrypt, "checkpw", spy)
        client = TestClient(web_server.app)  # 不進 context manager → 不觸發 lifespan（AICore 重初始化）
        resp = _post_login(client, "not-a-user", "whatever")
        assert resp.status_code == 303
        assert "error=invalid" in resp.headers["location"]
        assert len(calls) == 1
        assert calls[0] == web_server._DUMMY_BCRYPT_HASH.encode("utf-8")

    def test_unset_password_hash_runs_dummy_bcrypt(self, login_env, monkeypatch):
        """AUTH_PASSWORD_HASH 未設 → 正確帳號亦跑 dummy 比對（不洩初始化狀態）。"""
        from fastapi.testclient import TestClient

        monkeypatch.setattr(settings, "AUTH_PASSWORD_HASH", "")
        calls = []
        orig = bcrypt.checkpw

        def spy(pw, hashed):
            calls.append(hashed)
            return orig(pw, hashed)

        monkeypatch.setattr(web_server.bcrypt, "checkpw", spy)
        client = TestClient(web_server.app)  # 不觸發 lifespan
        resp = _post_login(client, "admin", "whatever")
        assert resp.status_code == 303
        assert "error=invalid" in resp.headers["location"]
        assert len(calls) == 1
        assert calls[0] == web_server._DUMMY_BCRYPT_HASH.encode("utf-8")

    def test_valid_username_wrong_password_runs_real_bcrypt(self, login_env, monkeypatch):
        """正確帳號錯誤密碼 → 跑正式 hash 比對（原判定邏輯不動）。"""
        from fastapi.testclient import TestClient

        real_hash = login_env
        calls = []
        orig = bcrypt.checkpw

        def spy(pw, hashed):
            calls.append(hashed)
            return orig(pw, hashed)

        monkeypatch.setattr(web_server.bcrypt, "checkpw", spy)
        client = TestClient(web_server.app)  # 不觸發 lifespan
        resp = _post_login(client, "admin", "wrong-password")
        assert resp.status_code == 303
        assert "error=invalid" in resp.headers["location"]
        assert len(calls) == 1
        assert calls[0] == real_hash.encode("utf-8")

    def test_successful_login_unchanged(self, login_env):
        """認證結果判定不可動：正確帳密仍成功登入、導向 /。"""
        from fastapi.testclient import TestClient

        client = TestClient(web_server.app)  # 不觸發 lifespan
        resp = _post_login(client, "admin", "correct-password")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/"

    def test_rate_limit_still_locks_with_forged_xff(self, login_env):
        """#3 端到端：直連（peer 非可信）連 5 次失敗帶不同偽造 XFF → 第 6 次鎖定。"""
        from fastapi.testclient import TestClient

        client = TestClient(web_server.app)  # 不觸發 lifespan
        for i in range(5):
            resp = client.post(
                "/login",
                data={"username": "admin", "password": "wrong"},
                headers={"X-Forwarded-For": f"10.9.8.{i}"},
                follow_redirects=False,
            )
            assert "error=invalid" in resp.headers["location"]
        resp = client.post(
            "/login",
            data={"username": "admin", "password": "wrong"},
            headers={"X-Forwarded-For": "10.9.8.99"},
            follow_redirects=False,
        )
        assert "error=locked" in resp.headers["location"]


# ── #4 CORS 收斂（C2）───────────────────────────────────────────────


def _cors_middleware_kwargs():
    """自 app.user_middleware 取 CORSMiddleware 之註冊參數。"""
    from fastapi.middleware.cors import CORSMiddleware

    for m in web_server.app.user_middleware:
        if m.cls is CORSMiddleware:
            return m.kwargs
    raise AssertionError("CORSMiddleware 未註冊")


class TestCorsRestriction:
    def test_settings_origins_explicit_and_no_wildcard(self):
        """settings.CORS_ALLOW_ORIGINS 為非空顯式清單、不含萬用字元。"""
        assert isinstance(settings.CORS_ALLOW_ORIGINS, list)
        assert settings.CORS_ALLOW_ORIGINS  # 非空
        assert "*" not in settings.CORS_ALLOW_ORIGINS

    def test_middleware_origins_not_wildcard(self):
        """CORSMiddleware allow_origins 已收斂＝settings 白名單、非 ["*"]。"""
        kwargs = _cors_middleware_kwargs()
        assert kwargs["allow_origins"] == settings.CORS_ALLOW_ORIGINS
        assert "*" not in kwargs["allow_origins"]

    def test_middleware_methods_headers_not_wildcard(self):
        """allow_methods / allow_headers 依需收斂、非萬用字元。"""
        kwargs = _cors_middleware_kwargs()
        assert "*" not in kwargs["allow_methods"]
        assert set(kwargs["allow_methods"]) == {"GET", "POST", "PATCH", "DELETE", "OPTIONS"}
        assert "*" not in kwargs["allow_headers"]

    def test_credentials_not_enabled(self):
        """allow_credentials 維持未啟用（不可動清單：嚴禁啟用）。"""
        kwargs = _cors_middleware_kwargs()
        assert kwargs.get("allow_credentials", False) is False

    def test_env_wildcard_is_filtered(self, monkeypatch):
        """env 誤設 "*" → settings 解析層剔除、不回退萬用。"""
        import importlib

        monkeypatch.setenv("CORS_ALLOW_ORIGINS", "*, https://ok.example.com ,")
        try:
            importlib.reload(settings)
            assert settings.CORS_ALLOW_ORIGINS == ["https://ok.example.com"]
            assert "*" not in settings.CORS_ALLOW_ORIGINS
        finally:
            # 還原：撤銷 env 後重載、防污染其他測試（settings 為模組級 config）
            monkeypatch.undo()
            importlib.reload(settings)

"""SEC-SECRET fail-closed 迴歸測試。

鎖定 SESSION_SECRET 的 fail-closed 行為，防未來 regression：
- 未設定 → 生成臨時隨機密鑰（絕不回退為可預測常數）+ SESSION_SECRET_IS_EPHEMERAL 旗標
- 已設定 → 逐字採用
- 硬編碼 fallback 常數必須從 web_server.py + settings.py 雙檔根除

註：production 未設 / 過弱 secret 的「拒絕啟動」發生在 web_server.py import 期，
以常數根除檢查 + settings 分支覆蓋即足；prod 啟動拒絕由手動 E2E 驗（見 hotfix 文件）。
"""
import importlib
import os

import pytest


@pytest.fixture(autouse=True)
def _restore_settings_module():
    """防測試污染：本檔 reload(settings) 會改 settings 模組單例狀態
    （ENVIRONMENT / SESSION_SECRET），teardown 必須把 env 還原並重新 reload，
    使 settings 回到真實環境狀態，避免污染其後 import settings 的測試檔。"""
    snapshot = {k: os.environ.get(k) for k in ("ENVIRONMENT", "SESSION_SECRET")}
    yield
    for k, v in snapshot.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    import settings
    importlib.reload(settings)


def _reload_settings(monkeypatch, env, secret):
    monkeypatch.setenv("ENVIRONMENT", env)
    if secret is None:
        monkeypatch.delenv("SESSION_SECRET", raising=False)
    else:
        monkeypatch.setenv("SESSION_SECRET", secret)
    import settings
    return importlib.reload(settings)


def test_dev_unset_generates_ephemeral_non_constant(monkeypatch):
    s = _reload_settings(monkeypatch, "development", None)
    assert s.SESSION_SECRET_IS_EPHEMERAL is True
    assert s.SESSION_SECRET and s.SESSION_SECRET != "insecure-dev-secret-change-me"
    assert len(s.SESSION_SECRET) >= 32           # secrets.token_urlsafe(48)


def test_set_secret_is_used_verbatim(monkeypatch):
    s = _reload_settings(monkeypatch, "production", "a-strong-real-secret-value-32chars++")
    assert s.SESSION_SECRET == "a-strong-real-secret-value-32chars++"
    assert s.SESSION_SECRET_IS_EPHEMERAL is False


def test_no_hardcoded_fallback_constant_in_source():
    # 硬編碼 fallback 常數必須從 web_server.py + settings.py 雙檔根除（防未來落回配置檔）
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for filename in ("web_server.py", "settings.py"):
        with open(os.path.join(root, filename), encoding="utf-8") as f:
            assert "insecure-dev-secret-change-me" not in f.read()

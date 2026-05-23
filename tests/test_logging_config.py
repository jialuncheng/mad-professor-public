"""LOGGING-1 階段：utils/logging_config.py 驗證。

依據:
- plan: .claude-logs/2026-05-23_logging_refactor_可行性評估.md v4
- §4.3 + §4.8-4.18 + §6 LOGGING-1 行
- 含 v3 陷阱 1+2 + v3 建議 1+2 + 補強 1/2/4 + v4 建議 1+2+3 全部 pytest case
"""
from __future__ import annotations

import importlib
import json
import logging
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ─────────────────── fixture ───────────────────


@pytest.fixture
def reset_logging_state():
    """重設 _logging_initialized + root handlers、避免 test 間互相污染。"""
    from utils.logging_config import reset_logging
    reset_logging()
    yield
    reset_logging()


def _make_record(level=logging.INFO, msg="test", exc_info=None, extra_fields=None):
    """製造 LogRecord（繞過真實 logger.x 呼叫、純測 Formatter）。"""
    record = logging.LogRecord(
        name="test_logger",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=None,
        exc_info=exc_info,
    )
    if extra_fields is not None:
        record.extra_fields = extra_fields
    return record


# ─────────────────── 1. v3 陷阱 1：ConsoleFormatter asctime（必修）───────────────────


def test_console_formatter_format_does_not_raise_attribute_error():
    """🔴 v3 陷阱 1: ConsoleFormatter.format() 必須先綁定 record.asctime、否則 AttributeError 啟動崩潰。"""
    from utils.logging_config import ConsoleFormatter
    fmt = ConsoleFormatter()
    record = _make_record()
    # 必須不拋 AttributeError
    result = fmt.format(record)
    assert "test" in result
    # 確認 asctime 被綁定
    assert hasattr(record, 'asctime')


# ─────────────────── 2. 補強 1：冪等性 ───────────────────


def test_setup_logging_idempotent(reset_logging_state):
    """補強 1: 多次 setup_logging() 不會掛重複 handler。"""
    from utils import logging_config
    logging_config.setup_logging()
    n_after_first = len(logging.getLogger().handlers)

    logging_config.setup_logging()
    logging_config.setup_logging()

    n_after_third = len(logging.getLogger().handlers)
    assert n_after_first == n_after_third


# ─────────────────── 3. 補強 2：第三方 logger 劫持 ───────────────────


def test_third_party_loggers_propagate_and_no_handlers(reset_logging_state):
    """補強 2: sqlalchemy.engine / uvicorn 全部 propagate=True、handler 清空。"""
    from utils.logging_config import setup_logging
    setup_logging()

    for name in ("sqlalchemy.engine", "uvicorn", "uvicorn.access", "uvicorn.error"):
        lg = logging.getLogger(name)
        assert lg.propagate is True
        assert len(lg.handlers) == 0


# ─────────────────── 4. v4 建議 1：SQLAlchemy / Uvicorn 噪聲分流 ───────────────────


def test_sqlalchemy_logger_silent_under_info_mode(monkeypatch, reset_logging_state):
    """v4 建議 1: root=INFO → sqlalchemy.engine.level == WARNING（防 SQL spam）。"""
    monkeypatch.setenv('LOG_LEVEL', 'INFO')

    import settings
    importlib.reload(settings)
    import utils.logging_config as lc
    importlib.reload(lc)

    lc.setup_logging()
    assert logging.getLogger("sqlalchemy.engine").level == logging.WARNING


def test_sqlalchemy_logger_verbose_under_debug_mode(monkeypatch, reset_logging_state):
    """v4 建議 1: root=DEBUG → sqlalchemy.engine.level == DEBUG（可看 SQL 細節）。"""
    monkeypatch.setenv('LOG_LEVEL', 'DEBUG')

    import settings
    importlib.reload(settings)
    import utils.logging_config as lc
    importlib.reload(lc)

    lc.setup_logging()
    assert logging.getLogger("sqlalchemy.engine").level == logging.DEBUG


def test_uvicorn_logger_follows_root_under_info(monkeypatch, reset_logging_state):
    """v4 建議 1: root=INFO → uvicorn.level == INFO（生命週期可見）。"""
    monkeypatch.setenv('LOG_LEVEL', 'INFO')

    import settings
    importlib.reload(settings)
    import utils.logging_config as lc
    importlib.reload(lc)

    lc.setup_logging()
    # min(WARNING=30, INFO=20) = 20 = INFO
    assert logging.getLogger("uvicorn").level == logging.INFO


# ─────────────────── 5. v4 建議 2：ContextVar 雙保險 ───────────────────


def test_contextvar_safe_in_cli_without_middleware():
    """v4 建議 2: CLI 場景無 middleware set、JSONFormatter 不拋 LookupError。"""
    from utils.logging_config import JSONFormatter, trace_context

    # 確認 ContextVar default 為 None
    assert trace_context.get(None) is None

    fmt = JSONFormatter()
    record = _make_record(msg="cli test")

    # 必須不拋 LookupError
    result = fmt.format(record)
    log_data = json.loads(result)
    assert log_data["message"] == "cli test"
    # 無 ctx 注入、不應有 trace_id key
    assert "trace_id" not in log_data


def test_contextvar_present_under_middleware():
    """v4 建議 2: middleware set ContextVar 後、Formatter 注入 trace_id。"""
    from utils.logging_config import JSONFormatter, trace_context

    token = trace_context.set({"trace_id": "abc-123", "owner_id": 42})
    try:
        fmt = JSONFormatter()
        record = _make_record(msg="request test")
        result = fmt.format(record)
        log_data = json.loads(result)
        assert log_data["trace_id"] == "abc-123"
        assert log_data["owner_id"] == 42
    finally:
        trace_context.reset(token)


# ─────────────────── 6. JSONFormatter Exception 結構化 + 安全防衛 ───────────────────


def test_jsonformatter_handles_real_exception():
    """補強 4: 真實 exception → 結構化 {type, message, stacktrace}。"""
    from utils.logging_config import JSONFormatter
    fmt = JSONFormatter()

    try:
        raise ValueError("test error")
    except ValueError:
        record = _make_record(
            level=logging.ERROR, msg="err", exc_info=sys.exc_info()
        )

    result = fmt.format(record)
    log_data = json.loads(result)

    assert "exception" in log_data
    assert log_data["exception"]["type"] == "ValueError"
    assert log_data["exception"]["message"] == "test error"
    assert "stacktrace" in log_data["exception"]


def test_jsonformatter_handles_empty_exc_info_tuple():
    """v3 建議 1: exc_info=(None, None, None) 不拋、不寫入 exception。"""
    from utils.logging_config import JSONFormatter
    fmt = JSONFormatter()

    record = _make_record(exc_info=(None, None, None))

    result = fmt.format(record)
    log_data = json.loads(result)
    assert "exception" not in log_data


# ─────────────────── 7. v4 建議 3：default=str 降級 ───────────────────


def test_jsonformatter_handles_unserializable_datetime():
    """v4 建議 3: extra={'ts': datetime} → JSON 內 ts 為 str、不拋 TypeError。"""
    from utils.logging_config import JSONFormatter
    fmt = JSONFormatter()

    record = _make_record(extra_fields={"ts": datetime(2026, 5, 23, 14, 0, 0)})

    result = fmt.format(record)
    log_data = json.loads(result)
    assert isinstance(log_data["ts"], str)
    assert "2026" in log_data["ts"]


def test_jsonformatter_handles_set_and_decimal():
    """v4 建議 3: set / Decimal 等 graceful。"""
    from utils.logging_config import JSONFormatter
    fmt = JSONFormatter()

    record = _make_record(extra_fields={"items": {1, 2, 3}, "amount": Decimal("19.99")})

    result = fmt.format(record)
    log_data = json.loads(result)
    assert isinstance(log_data["items"], str)
    assert isinstance(log_data["amount"], str)


def test_jsonformatter_preserves_standard_types():
    """v4 建議 3: 標準型別不受 default=str 影響。"""
    from utils.logging_config import JSONFormatter
    fmt = JSONFormatter()

    record = _make_record(
        extra_fields={"count": 42, "ratio": 3.14, "tags": ["a", "b"]}
    )

    result = fmt.format(record)
    log_data = json.loads(result)
    assert log_data["count"] == 42
    assert log_data["ratio"] == 3.14
    assert log_data["tags"] == ["a", "b"]


# ─────────────────── 8. v3 陷阱 2：uvicorn.run log_config=None ───────────────────


def test_uvicorn_run_passes_log_config_none():
    """🔴 v3 陷阱 2: web_server.py uvicorn.run 必須含 log_config=None。"""
    web_server_src = (ROOT / "web_server.py").read_text(encoding='utf-8')
    assert "log_config=None" in web_server_src, (
        "🔴 LOGGING-1 必修：web_server.py uvicorn.run 必須含 log_config=None、"
        "否則 uvicorn 預設 LOGGING_CONFIG dictConfig 會覆蓋 setup_logging() 配置"
    )


# ─────────────────── 9. settings env 整合 ───────────────────


def test_settings_log_level_default_info(monkeypatch):
    """settings.LOG_LEVEL 預設 INFO（Q4）。"""
    monkeypatch.delenv('LOG_LEVEL', raising=False)

    import settings
    importlib.reload(settings)

    assert settings.LOG_LEVEL == "INFO"


def test_settings_log_format_default_auto(monkeypatch):
    """settings.LOG_FORMAT 預設 auto（Q11）。"""
    monkeypatch.delenv('LOG_FORMAT', raising=False)

    import settings
    importlib.reload(settings)

    assert settings.LOG_FORMAT == "auto"

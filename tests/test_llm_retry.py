"""Tests for llm/retry.py decorators."""

import sys
import time
import random
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from llm.retry import retry_call, retry_stream, _is_retryable  # noqa: E402


class FakeCounter:
    """Helper: counts calls and raises N times before succeeding."""
    def __init__(self, fail_times: int, error: Exception, result='ok'):
        self.fail_times = fail_times
        self.error = error
        self.result = result
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise self.error
        return self.result


# ── _is_retryable ──

def test_is_retryable_5xx():
    assert _is_retryable(Exception('502 Bad Gateway'))
    assert _is_retryable(Exception('503 Service Unavailable'))
    assert _is_retryable(Exception('504 Gateway Timeout'))


def test_is_retryable_429():
    assert _is_retryable(Exception('429 Too Many Requests'))


def test_is_retryable_non_retryable():
    assert not _is_retryable(Exception('400 Bad Request'))
    assert not _is_retryable(Exception('401 Unauthorized'))
    assert not _is_retryable(ValueError('foo'))


# ── Phase 4.7d Commit 13：連線中斷 token 補洞 ──

def test_is_retryable_disconnect():
    """baron 觀察的「Server disconnected without sending a response.」應 retryable"""
    assert _is_retryable(Exception(
        'Server disconnected without sending a response.'))


def test_is_retryable_protocol_error():
    """httpx.RemoteProtocolError 及變體應 retryable"""
    assert _is_retryable(Exception('httpx.RemoteProtocolError: Server disconnected'))
    assert _is_retryable(Exception('Protocol Error: unexpected EOF'))


def test_is_retryable_reset():
    """connection reset / closed 應 retryable"""
    assert _is_retryable(Exception('connection reset by peer'))
    assert _is_retryable(Exception('Connection closed by remote host'))


# ── retry_call ──

def test_retry_call_5xx_then_success(monkeypatch):
    """502 一次後成功 → 重試 1 次、最終 ok。"""
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    counter = FakeCounter(fail_times=1, error=Exception('502 Bad Gateway'))

    @retry_call(retries=3)
    def fn():
        return counter()

    assert fn() == 'ok'
    assert counter.calls == 2  # 1 fail + 1 success


def test_retry_call_4xx_no_retry(monkeypatch):
    """400 立刻拋出、不重試。"""
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    counter = FakeCounter(fail_times=10, error=Exception('400 Bad Request'))

    @retry_call(retries=3)
    def fn():
        return counter()

    with pytest.raises(Exception, match='400'):
        fn()
    assert counter.calls == 1


def test_retry_call_exhausts(monkeypatch):
    """持續 503 → 重試 3 次後拋出（總 4 次 attempt）。"""
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    counter = FakeCounter(fail_times=10, error=Exception('503 Service Unavailable'))

    @retry_call(retries=3)
    def fn():
        return counter()

    with pytest.raises(Exception, match='503'):
        fn()
    assert counter.calls == 4  # retries + 1


def test_retry_call_429_retries(monkeypatch):
    """429 應重試（既有 chat_with_image 行為延續）。"""
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    counter = FakeCounter(fail_times=2, error=Exception('429 rate limit'))

    @retry_call(retries=3)
    def fn():
        return counter()

    assert fn() == 'ok'
    assert counter.calls == 3  # 2 fails + 1 success


def test_retry_call_non_retryable_value_error(monkeypatch):
    """ValueError 不重試。"""
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    counter = FakeCounter(fail_times=10, error=ValueError('foo'))

    @retry_call(retries=3)
    def fn():
        return counter()

    with pytest.raises(ValueError):
        fn()
    assert counter.calls == 1


def test_retry_call_backoff_timing(monkeypatch):
    """檢查 delay 序列符合 MODEL-9 Full Jitter（uniform 固定 0.5 驗證）。"""
    sleeps = []
    monkeypatch.setattr(time, 'sleep', lambda s: sleeps.append(s))
    # MODEL-9 後公式：delay = random.uniform(0, min(MAX, base*2^attempt))
    # 固定 random.uniform 回 0.5、與上界無關
    monkeypatch.setattr(random, 'uniform', lambda a, b: 0.5)
    counter = FakeCounter(fail_times=10, error=Exception('502'))

    @retry_call(retries=3, base=2.0)
    def fn():
        return counter()

    with pytest.raises(Exception):
        fn()

    # Full Jitter: random.uniform(0, exp_window) = 0.5（固定）
    # attempt 0/1/2 都同樣 0.5（因為 uniform 被 mock 固定回 0.5）
    assert sleeps == [0.5, 0.5, 0.5]


# ── retry_stream ──

def test_retry_stream_pre_yield_retry(monkeypatch):
    """generator 第一次 yield 前 raise '502' → 重啟成功。"""
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    calls = []

    @retry_stream(retries=3)
    def gen():
        calls.append(1)
        if len(calls) == 1:
            raise Exception('502 Bad Gateway')
        yield 'a'
        yield 'b'

    result = list(gen())
    assert result == ['a', 'b']
    assert len(calls) == 2  # 1 fail + 1 success


def test_retry_stream_mid_stream_no_retry(monkeypatch):
    """generator yield 1 個後 raise '502' → 立刻拋出、不重啟。"""
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    calls = []

    @retry_stream(retries=3)
    def gen():
        calls.append(1)
        yield 'a'
        raise Exception('502 Bad Gateway')

    items = []
    with pytest.raises(Exception, match='502'):
        for item in gen():
            items.append(item)

    assert items == ['a']
    assert len(calls) == 1  # 不重啟


def test_retry_stream_non_retryable_no_retry(monkeypatch):
    """generator raise ValueError → 立刻拋出、不重啟。"""
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    calls = []

    @retry_stream(retries=3)
    def gen():
        calls.append(1)
        raise ValueError('foo')
        yield  # 永遠到不了

    with pytest.raises(ValueError):
        list(gen())

    assert len(calls) == 1


# ─────────────────── MODEL-9 Full Jitter 測試 ───────────────────


def test_retry_call_full_random_jitter(monkeypatch):
    """MODEL-9: delay 應在 [0, exp_window] 區間、不是固定 base*2^attempt + jitter。"""
    from llm import retry as retry_mod
    captured = []
    monkeypatch.setattr(retry_mod.time, 'sleep', lambda d: captured.append(d))

    call_count = [0]

    @retry_call(retries=4, base=2.0)
    def flaky():
        call_count[0] += 1
        if call_count[0] < 5:
            raise ConnectionError("simulated connection drop")
        return "ok"

    flaky()
    # 4 次 retry 都觸發 sleep（attempt 0..3）
    assert len(captured) == 4
    # 每次 delay 都應在 [0, exp_window]、exp_window = min(MAX, base*2^attempt)
    for i, d in enumerate(captured):
        max_window = min(retry_mod.MAX_BACKOFF_SEC, 2.0 * (2 ** i))
        assert 0 <= d <= max_window, (
            f"attempt {i}: delay {d} 超出 [0, {max_window}]"
        )


def test_retry_call_max_backoff_cap(monkeypatch):
    """MODEL-9: attempt 大時 delay 不超過 MAX_BACKOFF_SEC。"""
    from llm import retry as retry_mod
    # 把 cap 改小、容易驗
    monkeypatch.setattr(retry_mod, 'MAX_BACKOFF_SEC', 10.0)
    captured = []
    monkeypatch.setattr(retry_mod.time, 'sleep', lambda d: captured.append(d))

    call_count = [0]

    @retry_call(retries=10, base=2.0)
    def flaky():
        call_count[0] += 1
        if call_count[0] < 11:
            raise ConnectionError("simulated connection drop")
        return "ok"

    flaky()
    # 後面 attempt（>= 3、base*2^3 = 16 > 10）應該都 cap 到 10
    for i, d in enumerate(captured):
        assert d <= 10.0, (
            f"attempt {i}: delay {d} > MAX_BACKOFF_SEC (10)"
        )

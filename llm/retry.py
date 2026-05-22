"""Retry helpers for LLM calls.

Provides two decorators:
- @retry_call: for synchronous callables (chat / chat_with_image)
- @retry_stream: for generator functions (chat_stream_by_sentence)

Both retry on transient errors (5xx, 429, timeout, connection) by matching
substrings in the exception message. Non-retryable errors (4xx, ValueError,
etc.) are raised immediately.

Backoff strategy: exponential with jitter.
  delay = base * (2 ** attempt) + random.uniform(0, 1)
"""

import functools
import logging
import os
import random
import time
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Phase 4.7? MODEL-9: Full Jitter 指數退避上限（避免 attempt 大時 wait 過久）
# 公式：t_wait = random(0, min(MAX_BACKOFF_SEC, base * 2^attempt))
# env override: LLM_RETRY_MAX_BACKOFF
MAX_BACKOFF_SEC = float(os.environ.get("LLM_RETRY_MAX_BACKOFF", 60.0))

# Retryable tokens matched against str(exception).lower()
_RETRYABLE_TOKENS = (
    '429',
    '500', '502', '503', '504',
    'timeout',
    'unavailable',
    'connection',
    'deadline',
    # Phase 4.7d Commit 13：補連線中斷相關 token——baron 連續上傳多份 paper
    # 觸發「Server disconnected without sending a response.」、retry 沒救
    # （'disconnect' 等不在原表內、被歸 non-retryable）。httpx / httpcore
    # 對連線中斷報的訊息變化多、多個關鍵字覆蓋。
    'disconnect',         # httpx「Server disconnected without sending a response.」
    'remote protocol',    # httpx.RemoteProtocolError
    'protocol error',     # 部分變體
    'incomplete read',    # 串流中斷
    'closed',             # connection closed
    'reset',              # connection reset by peer
)


def _is_retryable(e: Exception) -> bool:
    """Decide if an exception is retryable by matching substrings in its message."""
    s = str(e).lower()
    return any(tok in s for tok in _RETRYABLE_TOKENS)


def retry_call(retries: int = 3, base: float = 2.0):
    """Decorator: retry a synchronous callable on transient errors.

    Args:
        retries: max retry attempts (total calls = retries + 1)
        base: base delay seconds; actual delay = base * 2**attempt + jitter

    Behavior:
        - On retryable exception, log warning + sleep + retry
        - On non-retryable exception, raise immediately
        - When retries exhausted, raise the last exception (original type)
    """
    def deco(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(retries + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if attempt == retries or not _is_retryable(e):
                        raise
                    # MODEL-9: Full Jitter（取代線性抖動）
                    exp_window = min(MAX_BACKOFF_SEC, base * (2 ** attempt))
                    delay = random.uniform(0, exp_window)
                    logger.warning(
                        f"[{fn.__name__}] {type(e).__name__}: {e} — "
                        f"retry {attempt + 1}/{retries} after {delay:.1f}s"
                    )
                    time.sleep(delay)
        return wrapper
    return deco


def retry_stream(retries: int = 3, base: float = 2.0):
    """Decorator: retry a generator function on transient errors—only if
    no item has been yielded yet.

    Args:
        retries: max retry attempts
        base: base delay seconds

    Behavior:
        - If error occurs before any yield: retry from scratch (restart generator)
        - If error occurs after any yield: raise immediately (avoid duplicate output)
        - Non-retryable error: raise immediately regardless of state

    Caveat: the wrapped function must not have side-effects that conflict
    with restarting (LLM calls are read-only; safe).
    """
    def deco(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(retries + 1):
                yielded_any = False
                try:
                    for item in fn(*args, **kwargs):
                        yielded_any = True
                        yield item
                    return
                except Exception as e:
                    if yielded_any:
                        raise
                    if attempt == retries or not _is_retryable(e):
                        raise
                    # MODEL-9: Full Jitter（同 retry_call）
                    exp_window = min(MAX_BACKOFF_SEC, base * (2 ** attempt))
                    delay = random.uniform(0, exp_window)
                    logger.warning(
                        f"[{fn.__name__}] stream pre-yield {type(e).__name__}: "
                        f"{e} — retry {attempt + 1}/{retries} after {delay:.1f}s"
                    )
                    time.sleep(delay)
        return wrapper
    return deco

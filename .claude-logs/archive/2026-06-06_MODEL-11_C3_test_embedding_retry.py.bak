# === [MODEL-9-OPT C3 START] ===
"""MODEL-9-OPT C3：EmbeddingModel 限流與重試契約單元測試。

依據：plan §2.3 + tasks §8 C3。全程 mock `client.models.embed_content`（不實打 API）；
驗證 C2 重構後的彈性防禦框架：
- A embed_query 429 退避重試
- B embed_image 503 退避重試
- C embed_documents 批次重試耗盡 → 逐筆 _embed_one 降級（保序 + warning）
- D Semaphore 併發上限 ≤ EMBEDDING_MAX_CONCURRENT
"""
import logging
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from settings import EMBEDDING_MAX_CONCURRENT  # noqa: E402


def _make_instance_with_mock_client():
    """建 EmbeddingModel 實例、注入 mock client（繞 singleton + httpx 初始化）。
    `_api_semaphore` 為 class-level 屬性、實例自動共用（C2）。"""
    from config import EmbeddingModel
    instance = EmbeddingModel.__new__(EmbeddingModel)
    instance.client = MagicMock()
    instance.model = "gemini-embedding-2"
    instance.logger = logging.getLogger("config")
    return instance


def _resp(values):
    """構造 embed_content 回傳替身（embeddings[i].values）。"""
    resp = MagicMock()
    resp.embeddings = [MagicMock(values=v) for v in values]
    return resp


# ─────────────────── A. embed_query 429 退避 ───────────────────


def test_embed_query_retry_success(monkeypatch):
    """A：embed_query 首呼 429、次呼成功 → @retry_call 退避後回 normalized。"""
    monkeypatch.setattr(time, "sleep", lambda *a, **k: None)  # 加速：跳過退避 sleep
    instance = _make_instance_with_mock_client()

    calls = {"n": 0}

    def side_effect(**kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise Exception("429 RESOURCE_EXHAUSTED")
        return _resp([[3.0, 4.0]])

    instance.client.models.embed_content.side_effect = side_effect

    result = instance.embed_query("test query")

    assert calls["n"] == 2                                   # 重試 1 次後成功
    assert pytest.approx(np.linalg.norm(result), abs=1e-5) == 1.0   # normalized


# ─────────────────── B. embed_image 503 重試 ───────────────────


def test_embed_image_retry_success(monkeypatch):
    """B：embed_image 首呼 503、次呼成功 → @retry_call 退避後回 normalized。"""
    monkeypatch.setattr(time, "sleep", lambda *a, **k: None)
    instance = _make_instance_with_mock_client()

    calls = {"n": 0}

    def side_effect(**kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise Exception("503 Service Unavailable")
        return _resp([[3.0, 4.0]])

    instance.client.models.embed_content.side_effect = side_effect

    result = instance.embed_image(b"fake-image-bytes", mime_type="image/jpeg")

    assert calls["n"] == 2
    assert pytest.approx(np.linalg.norm(result), abs=1e-5) == 1.0


# ─────────────────── C. embed_documents 批次降級保序 ───────────────────


def test_embed_documents_fallback_on_error(monkeypatch, caplog):
    """C：批次（contents>1）持續 429 → 重試耗盡 → 降級逐筆 _embed_one（保序）+ warning。"""
    monkeypatch.setattr(time, "sleep", lambda *a, **k: None)
    instance = _make_instance_with_mock_client()

    single_vecs = {"a": [1.0, 0.0], "b": [0.0, 1.0]}

    def side_effect(**kwargs):
        contents = kwargs.get("contents")
        if len(contents) > 1:                               # 批次呼叫 → 永遠 429
            raise Exception("429 RESOURCE_EXHAUSTED")
        return _resp([single_vecs[contents[0]]])            # 逐筆 → 成功、依文字回固定向量

    instance.client.models.embed_content.side_effect = side_effect

    with caplog.at_level(logging.WARNING):
        results = instance.embed_documents(["a", "b"])

    # 降級成功、回兩筆 normalized 且順序對齊（a→[1,0]、b→[0,1]）
    assert len(results) == 2
    assert pytest.approx(results[0][0], abs=1e-5) == 1.0 and pytest.approx(results[0][1], abs=1e-5) == 0.0
    assert pytest.approx(results[1][0], abs=1e-5) == 0.0 and pytest.approx(results[1][1], abs=1e-5) == 1.0
    assert "逐筆" in caplog.text                            # 降級 warning 已輸出


# ─────────────────── D. Semaphore 併發上限 ───────────────────


def test_embedding_semaphore_concurrency_limit():
    """D：高併發 embed_query 時，同時進入底層 API 的數量 ≤ EMBEDDING_MAX_CONCURRENT。"""
    instance = _make_instance_with_mock_client()

    state = {"cur": 0, "max": 0}
    lock = threading.Lock()

    def side_effect(**kwargs):
        with lock:
            state["cur"] += 1
            state["max"] = max(state["max"], state["cur"])
        time.sleep(0.05)                                    # 製造重疊窗口（真 sleep）
        with lock:
            state["cur"] -= 1
        return _resp([[1.0, 0.0]])

    instance.client.models.embed_content.side_effect = side_effect

    n_threads = EMBEDDING_MAX_CONCURRENT * 2 + 2            # 遠超上限以逼出排隊
    with ThreadPoolExecutor(max_workers=n_threads) as ex:
        list(ex.map(lambda _: instance.embed_query("q"), range(n_threads)))

    assert state["max"] >= 1                                 # 確有併發
    assert state["max"] <= EMBEDDING_MAX_CONCURRENT          # 受 Semaphore 限制
# === [MODEL-9-OPT C3 END] ===

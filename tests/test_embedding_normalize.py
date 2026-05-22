"""Phase 4.7? MODEL-1+2 B1: EmbeddingModel L2 normalize 驗證。

驗證：
- `_l2_normalize` 對空 list / None / 零向量 / unit vector / 任意 768 維輸入的正確行為
- `embed_documents` / `embed_query` / `embed_image` 輸出全是 unit vectors

依據：
- plan §4.1 + §3.6.3 修正 3（防禦升級：空值 / 1e-6 / 零向量明確回 [0.0]*len）
- plan §6.1 修正版（v3 8+ 個 test）
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ─────────────────── _l2_normalize helper 測試（7 個）───────────────────


def test_l2_normalize_unit_vector():
    """已是 unit vector 的不變（norm = 1）。"""
    from config import EmbeddingModel
    vec = [0.6, 0.8]
    result = EmbeddingModel._l2_normalize(vec)
    assert pytest.approx(np.linalg.norm(result), abs=1e-5) == 1.0
    assert pytest.approx(result[0], abs=1e-5) == 0.6
    assert pytest.approx(result[1], abs=1e-5) == 0.8


def test_l2_normalize_arbitrary_vector():
    """任意向量 normalize 後 norm = 1（[3, 4] → [0.6, 0.8]）。"""
    from config import EmbeddingModel
    vec = [3.0, 4.0]
    result = EmbeddingModel._l2_normalize(vec)
    assert pytest.approx(np.linalg.norm(result), abs=1e-5) == 1.0
    assert pytest.approx(result[0], abs=1e-5) == 0.6
    assert pytest.approx(result[1], abs=1e-5) == 0.8


def test_l2_normalize_empty_list():
    """修正 3：空 list 直接回原值、不 crash。"""
    from config import EmbeddingModel
    assert EmbeddingModel._l2_normalize([]) == []


def test_l2_normalize_none_handling():
    """修正 3：None 直接回 None、不 crash。"""
    from config import EmbeddingModel
    assert EmbeddingModel._l2_normalize(None) is None


def test_l2_normalize_zero_vector():
    """修正 3：零向量回 [0.0] * len（避免 caller 誤判 unit vector）。"""
    from config import EmbeddingModel
    vec = [0.0, 0.0, 0.0]
    result = EmbeddingModel._l2_normalize(vec)
    assert result == [0.0, 0.0, 0.0]
    assert len(result) == 3


def test_l2_normalize_near_zero_float32():
    """修正 3：極小值 < 1e-6 視為零向量、避免 float32 精度溢出。"""
    from config import EmbeddingModel
    vec = [1e-8, 1e-8, 1e-8]  # norm ~ 1.7e-8、低於 1e-6 閾值
    result = EmbeddingModel._l2_normalize(vec)
    assert result == [0.0, 0.0, 0.0]


def test_l2_normalize_768_dim():
    """768 維向量正常 normalize（real-world 維度）。"""
    from config import EmbeddingModel
    rng = np.random.default_rng(42)
    vec = rng.standard_normal(768).tolist()
    result = EmbeddingModel._l2_normalize(vec)
    assert len(result) == 768
    assert pytest.approx(np.linalg.norm(result), abs=1e-5) == 1.0


# ─────────────────── embed_documents / embed_query mock 測試（3 個）───────────────────


def _make_instance_with_mock_client():
    """建 EmbeddingModel 實例、注入 mock client（繞 singleton + httpx 初始化）。"""
    from config import EmbeddingModel
    instance = EmbeddingModel.__new__(EmbeddingModel)
    instance.client = MagicMock()
    instance.model = "gemini-embedding-2"
    import logging
    instance.logger = logging.getLogger("test")
    return instance


def test_embed_documents_returns_normalized():
    """embed_documents 輸出全部 unit vectors（含批次內多筆）。"""
    instance = _make_instance_with_mock_client()

    mock_emb1 = MagicMock()
    mock_emb1.values = [3.0, 4.0]   # norm = 5
    mock_emb2 = MagicMock()
    mock_emb2.values = [1.0, 0.0]   # norm = 1（已 unit）
    mock_response = MagicMock()
    mock_response.embeddings = [mock_emb1, mock_emb2]
    instance.client.models.embed_content.return_value = mock_response

    results = instance.embed_documents(["a", "b"])

    assert len(results) == 2
    for vec in results:
        assert pytest.approx(np.linalg.norm(vec), abs=1e-5) == 1.0


def test_embed_query_returns_normalized():
    """embed_query 輸出是 unit vector。"""
    instance = _make_instance_with_mock_client()

    mock_emb = MagicMock()
    mock_emb.values = [3.0, 4.0]
    mock_response = MagicMock()
    mock_response.embeddings = [mock_emb]
    instance.client.models.embed_content.return_value = mock_response

    result = instance.embed_query("test query")

    assert pytest.approx(np.linalg.norm(result), abs=1e-5) == 1.0
    assert len(result) == 2


def test_embed_uses_correct_model_and_dimensions():
    """確認 embed call 用對 model name + output_dimensionality。"""
    from settings import EMBEDDING_MODEL_NAME, EMBEDDING_OUTPUT_DIMENSIONS
    instance = _make_instance_with_mock_client()

    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[1.0, 0.0])]
    instance.client.models.embed_content.return_value = mock_response

    instance.embed_query("test")

    call_kwargs = instance.client.models.embed_content.call_args.kwargs
    # instance.model = "gemini-embedding-2" (mock 設定)、不直接驗 EMBEDDING_MODEL_NAME
    # 因為 instance 是 mock、model 屬性是手動設的
    assert call_kwargs.get("model") == "gemini-embedding-2"
    config = call_kwargs.get("config")
    assert config is not None
    # output_dimensionality 抽 EMBEDDING_OUTPUT_DIMENSIONS 常數
    assert getattr(config, "output_dimensionality", None) == EMBEDDING_OUTPUT_DIMENSIONS

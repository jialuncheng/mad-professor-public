"""Phase 4.7? MODEL-3 修正 5: TILING_MAX_LENGTH env override 驗證。

依據：plan §4.6 修正 5
"""
import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_env_override_tiling_max_length(monkeypatch):
    """TILING_MAX_LENGTH=5000 → __init__(max_length=None) 用 5000 為預設。"""
    monkeypatch.setenv('TILING_MAX_LENGTH', '5000')

    import settings
    importlib.reload(settings)
    import processor.tiling_processor
    importlib.reload(processor.tiling_processor)

    from processor.tiling_processor import TilingProcessor
    p = TilingProcessor(min_length=500, max_length=None, embedder=None)
    assert p.max_length == 5000


def test_explicit_max_length_overrides_env(monkeypatch):
    """caller 顯式傳 max_length=3000 仍生效（backward compat、env 不蓋）。"""
    monkeypatch.setenv('TILING_MAX_LENGTH', '5000')

    import settings
    importlib.reload(settings)
    import processor.tiling_processor
    importlib.reload(processor.tiling_processor)

    from processor.tiling_processor import TilingProcessor
    p = TilingProcessor(min_length=500, max_length=3000, embedder=None)
    assert p.max_length == 3000

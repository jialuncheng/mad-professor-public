"""RAG-1 Phase 2 P2-1：雙語摘要管道 pytest（3 個）。

驗收：
1. metadata_extractor._ALL_FIELDS / create_empty_metadata 含 translated_abstract
2. pipeline_core._stage_translate 完成後寫入 self._metadata["translated_abstract"]
3. translate_processor.translated_abstract 為空 / None 時、_metadata 不破（fallback safe）
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from processor.metadata_extractor import (  # noqa: E402
    _ALL_FIELDS,
    create_empty_metadata,
)
from pipeline_core import PipelineCore  # noqa: E402


def test_metadata_extractor_includes_translated_abstract_field():
    """P2-1 #1: _ALL_FIELDS 與 create_empty_metadata 含 translated_abstract。"""
    assert "translated_abstract" in _ALL_FIELDS, (
        "_ALL_FIELDS 應含 translated_abstract（P2-1 新增）"
    )
    meta = create_empty_metadata()
    assert "translated_abstract" in meta
    field = meta["translated_abstract"]
    # 對齊既有 schema v2 結構（value / source / confidence / alternates）
    assert isinstance(field, dict)
    assert field["value"] is None
    assert field["source"] is None
    assert field["confidence"] is None
    assert field["alternates"] == {}


def test_pipeline_writes_translated_abstract_after_translate(tmp_path):
    """P2-1 #2: translate stage 完成後從 translate_processor.translated_abstract
    寫進 self._metadata、source=translate_pipeline、confidence=high。"""
    pc = PipelineCore()
    pc._metadata = create_empty_metadata()

    # mock translate_processor：return 任意值、translated_abstract 屬性給定中文
    mock_tp = MagicMock()
    mock_tp.translated_abstract = "這是翻譯後的中文摘要"
    mock_tp.process.return_value = str(tmp_path / "translate_out.json")
    pc._translate_processor = mock_tp

    # mock tiling input 與 output 路徑
    tiling_in = tmp_path / "tiling.json"
    tiling_in.write_text("{}", encoding="utf-8")
    pc.paper_info = {"paper_id": "p1", "output_dir": str(tmp_path)}

    output_paths = {
        "tiling": str(tiling_in),
        "_confirmed_doc_type": "academic",
        "_domain": "ml",
    }
    pc._stage_translate(None, tmp_path, "p1", output_paths)

    # 驗證寫入
    field = pc._metadata.get("translated_abstract")
    assert isinstance(field, dict)
    assert field["value"] == "這是翻譯後的中文摘要"
    assert field["source"] == "translate_pipeline"
    assert field["confidence"] == "high"


def test_pipeline_translated_abstract_none_does_not_break(tmp_path):
    """P2-1 #3: translate_processor.translated_abstract 為空 / None 時、
    _metadata 不寫入、原本的 None 結構保留、整個 _stage_translate 不 raise。"""
    pc = PipelineCore()
    pc._metadata = create_empty_metadata()

    mock_tp = MagicMock()
    mock_tp.translated_abstract = ""  # 空字串、translate 失敗或未產出
    mock_tp.process.return_value = str(tmp_path / "translate_out.json")
    pc._translate_processor = mock_tp

    tiling_in = tmp_path / "tiling.json"
    tiling_in.write_text("{}", encoding="utf-8")
    pc.paper_info = {"paper_id": "p2", "output_dir": str(tmp_path)}

    output_paths = {
        "tiling": str(tiling_in),
        "_confirmed_doc_type": "academic",
        "_domain": "",
    }
    # 不應 raise
    pc._stage_translate(None, tmp_path, "p2", output_paths)

    field = pc._metadata.get("translated_abstract")
    # 結構仍在、value 仍為 None（沒被空字串覆寫）
    assert isinstance(field, dict)
    assert field["value"] is None
    assert field["source"] is None

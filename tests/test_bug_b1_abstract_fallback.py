"""RAG-1 BUG-B1：後端 abstract fallback pytest（依評估 v4 §B Bug 8）。

涵蓋：
- 方案 A（pipeline_core）：translate_processor.translated_abstract 為空且
  metadata.abstract.value 有英文 → 側路 translate_text 翻譯、寫進 _metadata
- 方案 A 防禦：translate_text 抛例外 → 不破 P2-1 主流程、translated_abstract 保留空
- 方案 A 邊界：metadata.abstract 不是 dict → 不 raise、type-safe
- 方案 B（md_processor）：abstract_pattern 匹配中文「摘要 / 概要 / 內容提要 /
  内容提要」+ 日文「要旨」+ 既有英文模式仍 work
- 相容性：跟 P2-1 ship 路徑共存、translated_abstract 非空時直接走原路徑（不誤觸 side-channel）
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from processor.metadata_extractor import create_empty_metadata  # noqa: E402
from processor.md_processor import MarkdownProcessor  # noqa: E402
from pipeline_core import PipelineCore  # noqa: E402


# ─────────────────── 方案 A：pipeline_core 側路 fallback ───────────────────


def test_a_side_channel_triggers_when_translate_processor_empty_and_meta_abstract_exists(tmp_path):
    """A：translated_abstract 為空、metadata.abstract.value 有英文時、
    側路呼叫 translate_text("abstract", eng) 翻譯後寫入 _metadata。"""
    pc = PipelineCore()
    pc._metadata = create_empty_metadata()
    # metadata.abstract.value 有英文（模擬 Stage A/B 已抽取、但 md_processor 沒匹配到）
    pc._metadata["abstract"]["value"] = "This paper presents a novel approach to ..."

    mock_tp = MagicMock()
    mock_tp.translated_abstract = ""   # 翻譯失敗 / 未抽取
    mock_tp.process.return_value = str(tmp_path / "out.json")
    # 側路呼叫應觸發、回中文翻譯
    mock_tp.translate_text.return_value = "這篇論文提出一種新方法 ..."
    pc._translate_processor = mock_tp

    tiling_in = tmp_path / "tiling.json"
    tiling_in.write_text("{}", encoding="utf-8")
    pc.paper_info = {"paper_id": "p_side", "output_dir": str(tmp_path)}

    output_paths = {"tiling": str(tiling_in), "_confirmed_doc_type": "academic", "_domain": ""}
    pc._stage_translate(None, tmp_path, "p_side", output_paths)

    # 驗證側路 translate_text 被呼叫、參數正確
    mock_tp.translate_text.assert_called_once_with(
        "abstract", "This paper presents a novel approach to ..."
    )
    # _metadata 寫入翻譯後內容
    field = pc._metadata.get("translated_abstract")
    assert isinstance(field, dict)
    assert field["value"] == "這篇論文提出一種新方法 ..."
    assert field["source"] == "translate_pipeline"


def test_a_side_channel_failure_does_not_break_pipeline(tmp_path):
    """A 防禦：side-channel translate_text raise → 內層 try/except 包覆、
    translated_abstract 保留空、_stage_translate 不 raise（P2-1 主流程不破）。"""
    pc = PipelineCore()
    pc._metadata = create_empty_metadata()
    pc._metadata["abstract"]["value"] = "Some English abstract"

    mock_tp = MagicMock()
    mock_tp.translated_abstract = ""
    mock_tp.process.return_value = str(tmp_path / "out.json")
    mock_tp.translate_text.side_effect = RuntimeError("LLM API down")
    pc._translate_processor = mock_tp

    tiling_in = tmp_path / "tiling.json"
    tiling_in.write_text("{}", encoding="utf-8")
    pc.paper_info = {"paper_id": "p_fail", "output_dir": str(tmp_path)}

    output_paths = {"tiling": str(tiling_in), "_confirmed_doc_type": "academic", "_domain": ""}
    # 不應 raise
    pc._stage_translate(None, tmp_path, "p_fail", output_paths)

    # translated_abstract 保留 None（外層 if 條件 falsy、不寫入）
    field = pc._metadata.get("translated_abstract")
    assert isinstance(field, dict)
    assert field["value"] is None


def test_a_side_channel_no_eng_abstract_skips(tmp_path):
    """A 邊界：translated_abstract 空 + metadata.abstract.value 也空 → side-channel 不觸發、
    translate_text 不應呼叫、_metadata 不寫入。"""
    pc = PipelineCore()
    pc._metadata = create_empty_metadata()
    # 既有 metadata.abstract.value = None（create_empty_metadata 預設）

    mock_tp = MagicMock()
    mock_tp.translated_abstract = ""
    mock_tp.process.return_value = str(tmp_path / "out.json")
    pc._translate_processor = mock_tp

    tiling_in = tmp_path / "tiling.json"
    tiling_in.write_text("{}", encoding="utf-8")
    pc.paper_info = {"paper_id": "p_empty", "output_dir": str(tmp_path)}

    output_paths = {"tiling": str(tiling_in), "_confirmed_doc_type": "academic", "_domain": ""}
    pc._stage_translate(None, tmp_path, "p_empty", output_paths)

    mock_tp.translate_text.assert_not_called()
    field = pc._metadata.get("translated_abstract")
    assert field["value"] is None


def test_a_side_channel_type_safe_when_abstract_not_dict(tmp_path):
    """A 防禦：metadata.abstract 不是 dict（如 None / string、模擬 schema 變動）→
    type-safe check 不 raise、side-channel 不誤觸發。"""
    pc = PipelineCore()
    pc._metadata = create_empty_metadata()
    pc._metadata["abstract"] = "raw_string_not_dict"   # 模擬畸形 schema

    mock_tp = MagicMock()
    mock_tp.translated_abstract = ""
    mock_tp.process.return_value = str(tmp_path / "out.json")
    pc._translate_processor = mock_tp

    tiling_in = tmp_path / "tiling.json"
    tiling_in.write_text("{}", encoding="utf-8")
    pc.paper_info = {"paper_id": "p_malformed", "output_dir": str(tmp_path)}

    output_paths = {"tiling": str(tiling_in), "_confirmed_doc_type": "academic", "_domain": ""}
    # 不應 raise（isinstance check 防禦）
    pc._stage_translate(None, tmp_path, "p_malformed", output_paths)

    mock_tp.translate_text.assert_not_called()


def test_a_p2_1_compat_truthy_translated_abstract_bypasses_side_channel(tmp_path):
    """相容性：P2-1 ship 路徑——translated_abstract 非空時直接走原寫入路徑、
    side-channel 不觸發（不破壞 P2-1 既有行為）。"""
    pc = PipelineCore()
    pc._metadata = create_empty_metadata()
    pc._metadata["abstract"]["value"] = "Some English abstract"

    mock_tp = MagicMock()
    mock_tp.translated_abstract = "已存在的中文翻譯"   # P2-1 path: translate_processor 正常出值
    mock_tp.process.return_value = str(tmp_path / "out.json")
    pc._translate_processor = mock_tp

    tiling_in = tmp_path / "tiling.json"
    tiling_in.write_text("{}", encoding="utf-8")
    pc.paper_info = {"paper_id": "p_p21", "output_dir": str(tmp_path)}

    output_paths = {"tiling": str(tiling_in), "_confirmed_doc_type": "academic", "_domain": ""}
    pc._stage_translate(None, tmp_path, "p_p21", output_paths)

    # translate_text 不應被呼叫（既有非空、不需 side-channel）
    mock_tp.translate_text.assert_not_called()
    # _metadata 用 P2-1 path 寫入
    field = pc._metadata.get("translated_abstract")
    assert field["value"] == "已存在的中文翻譯"
    assert field["source"] == "translate_pipeline"


# ─────────────────── 方案 B：md_processor regex 擴中文 + 日文 ───────────────────


@pytest.fixture
def md_proc():
    return MarkdownProcessor()


@pytest.mark.parametrize("heading", [
    "# Abstract",
    "## Abstract",
    "## ABSTRACT",
    "## summary",
    "### Summary",
    "# 1. Abstract",
    "## 2. SUMMARY",
])
def test_b_abstract_pattern_matches_legacy_english(md_proc, heading):
    """B 相容性：既有英文 pattern 仍 work（無迴歸）。"""
    assert md_proc.abstract_pattern.match(heading), f'應匹配既有英文 heading: {heading!r}'


@pytest.mark.parametrize("heading", [
    "## 摘要",
    "### 摘要",
    "# 摘要",
    "## 1. 摘要",
    "## 概要",
    "### 概要",
    "## 內容提要",   # 繁中
    "## 内容提要",   # 簡中
    "## 要旨",       # 日文
])
def test_b_abstract_pattern_matches_chinese_japanese(md_proc, heading):
    """B 新增：中文 / 日文 heading 匹配。"""
    assert md_proc.abstract_pattern.match(heading), f'應匹配中日文 heading: {heading!r}'


@pytest.mark.parametrize("heading", [
    "## Introduction",
    "## 緒論",
    "## 引言",
    "## References",
    "## 結論",
    "## 梗概",         # v3 Q8：古文罕見、不含
    "## 大綱",
])
def test_b_abstract_pattern_does_not_match_non_abstract(md_proc, heading):
    """B 邊界：非 abstract heading 不誤匹（含 v3 Q8 「梗概」不含）。"""
    assert not md_proc.abstract_pattern.match(heading), (
        f'不應誤匹非 abstract heading: {heading!r}'
    )

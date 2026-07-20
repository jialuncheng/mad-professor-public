"""PIPE-INGEST-FITZ C2 — 連字修復純函式單元測試。

覆蓋：壞字正修（`Pro1les`/`;rst`/`de1ning`）、雙閘防誤殺（數字縮寫/
版本號/中文）、行數不變式、系統字典缺席時內建兜底集語意。
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pipelines.ligature_repair as lr  # noqa: E402
from pipelines.ligature_repair import repair_ligatures  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_word_cache():
    """每測試重置 lazy 字典快取（隔離 monkeypatch 場景）。"""
    lr._word_cache = None
    yield
    lr._word_cache = None


class TestRepair:
    def test_pro1les_to_profiles(self):
        assert repair_ligatures("Executive Pro1les of the firm") == \
            "Executive Profiles of the firm"

    def test_semicolon_rst_to_first(self):
        assert repair_ligatures("the ;rst quarter") == "the first quarter"

    def test_de1ning_to_defining(self):
        assert repair_ligatures("a de1ning moment") == "a defining moment"

    def test_punctuation_wrapped_token(self):
        assert repair_ligatures('(the "Pro1les," he said)') == \
            '(the "Profiles," he said)'

    def test_multiple_bad_tokens_one_line(self):
        assert repair_ligatures("de1ning the ;rst Pro1les") == \
            "defining the first Profiles"


class TestDoubleGate:
    @pytest.mark.parametrize("token", ["1st", "2nd", "3rd", "4th", "10s"])
    def test_gate1_numeric_abbreviations_untouched(self, token):
        line = f"the {token} item"
        assert repair_ligatures(line) == line

    @pytest.mark.parametrize("token", ["v1", "v1.2", "v12.3.4"])
    def test_gate1_version_numbers_untouched(self, token):
        line = f"release {token} shipped"
        assert repair_ligatures(line) == line

    def test_uppercase_context_untouched(self):
        line = "the M1 晶片 and A1 grade"  # 大寫×數字：非窗口形態
        assert repair_ligatures(line) == line

    def test_chinese_line_untouched(self):
        line = "這是一行繁體中文內容，含全形；分號與數字 1 混排。"
        assert repair_ligatures(line) == line

    def test_gate2_invalid_result_kept_asis(self):
        line = "code b1g and x;z tokens"  # 替換後非有效詞 → fail-open 保留
        assert repair_ligatures(line) == line

    def test_legit_digit_inside_identifier_untouched(self):
        line = "call func1x variable"  # fi→"funcfix"? 非有效詞 → 保留
        assert repair_ligatures(line) == line


class TestLineInvariant:
    def test_line_count_and_blank_lines_preserved(self):
        text = "Title\n\nthe ;rst body\n\n\nPro1les tail\n"
        out = repair_ligatures(text)
        assert out.count("\n") == text.count("\n")
        assert out.splitlines()[2] == "the first body"
        assert out.split("\n")[1] == ""  # 空行原位保留

    def test_pure_function_no_side_effect(self):
        text = "no bad chars here"
        assert repair_ligatures(text) == text


class TestDictionaryFallback:
    def test_fallback_set_used_when_system_dict_missing(self, monkeypatch):
        monkeypatch.setattr(
            lr, "_SYSTEM_DICT_PATH", Path("/nonexistent/dict/words")
        )
        assert repair_ligatures("a de1ning ;rst Pro1les") == \
            "a defining first Profiles"  # 內建兜底集仍正修

    def test_system_dict_loaded_and_cached_once(self, tmp_path, monkeypatch):
        fake_dict = tmp_path / "words"
        fake_dict.write_text("flourish\n", encoding="utf-8")
        monkeypatch.setattr(lr, "_SYSTEM_DICT_PATH", fake_dict)
        # "1ourish" 僅系統字典收錄（fl 候選）→ 證明優先載入系統字典
        assert repair_ligatures("plants 1ourish here") == "plants flourish here"
        first = lr._word_set()
        assert lr._word_set() is first  # lazy 一次快取

    def test_dict_read_failure_degrades_to_fallback(self, monkeypatch):
        # 目錄：exists=True 但 read_text 拋 IsADirectoryError → 降級兜底集
        monkeypatch.setattr(lr, "_SYSTEM_DICT_PATH", Path("/etc"))
        assert repair_ligatures("the ;rst item") == "the first item"

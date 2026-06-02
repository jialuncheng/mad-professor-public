"""GOLDEN-BASELINE OP-2 比對引擎單元測試（plan v2 §6.1）。

以合成資料覆蓋三維度 Diff（D1 結構樹／D2 相似度／D3 Jaccard）、影子雜訊正規化、
紅綠燈裁決彙總、checksum 防竄改、改善豁免分支。**不需 MinerU / 真實 golden 快照**。
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools"))

import golden_baseline as gb  # noqa: E402


# ── D1 排版結構樹 ──

def test_d1_identical_no_degradation():
    md = "# Title\n\n## Sec A\n\n- item1\n- item2\n\n![alt](img.png)\n"
    g = {"D1_zh": md, "D1_en": md}
    c = {"D1_zh": md, "D1_en": md}
    assert gb._diff_d1(g, c)["degraded"] is False


def test_d1_heading_removed_is_degradation():
    base = "# Title\n\n## Sec A\n\n## Sec B\n"
    cand = "# Title\n\n## Sec A\n"  # 少一個 heading
    r = gb._diff_d1({"D1_zh": base, "D1_en": base}, {"D1_zh": cand, "D1_en": cand})
    assert r["degraded"] is True
    assert any("heading" in d for d in r["deltas"])


def test_d1_table_rows_diff_is_degradation():
    base = "| a | b |\n| 1 | 2 |\n| 3 | 4 |\n"
    cand = "| a | b |\n| 1 | 2 |\n"  # 少一行
    r = gb._diff_d1({"D1_zh": base, "D1_en": base}, {"D1_zh": cand, "D1_en": cand})
    assert r["degraded"] is True


def test_d1_image_alt_mismatch_is_degradation():
    base = "![diagram](a.png)\n"
    cand = "![chart](a.png)\n"  # alt 文字不同
    r = gb._diff_d1({"D1_zh": base, "D1_en": base}, {"D1_zh": cand, "D1_en": cand})
    assert r["degraded"] is True
    assert any("alt" in d for d in r["deltas"])


# ── 影子雜訊正規化 ──

def test_normalize_strips_shadow_test_suffix_and_timestamp():
    raw = "標題 (測試)_shadow 產出於 2026-06-02 12:42:01"
    norm = gb._normalize_text(raw)
    assert "(測試)" not in norm
    assert "_shadow" not in norm
    assert "2026-06-02" not in norm


def test_d1_shadow_noise_normalized_equivalent():
    base = "# 報告\n\n## 章節\n"
    cand = "# 報告 (測試)\n\n## 章節\n"  # 僅影子後綴差異
    r = gb._diff_d1({"D1_zh": base, "D1_en": base}, {"D1_zh": cand, "D1_en": cand})
    assert r["degraded"] is False  # 正規化後等價


# ── D2 譯文相似度 ──

def _tree(*sections):
    return {"sections": list(sections)}


def test_d2_identical_pass():
    t = _tree("這是第一段譯文。", "這是第二段譯文。")
    r = gb._diff_d2(t, t)
    assert r["degraded"] is False
    assert r["min_similarity"] == 1.0


def test_d2_section_count_mismatch_fail():
    g = _tree("a", "b", "c")
    c = _tree("a", "b")
    r = gb._diff_d2(g, c)
    assert r["degraded"] is True
    assert r["reason"] == "section_count_mismatch"


def test_d2_low_similarity_fail():
    g = _tree("這是一段完整且正確的中文譯文內容描述。")
    c = _tree("完全不同的另一段文字毫無關聯。")
    r = gb._diff_d2(g, c)
    assert r["degraded"] is True
    assert r["min_similarity"] < gb._D2_SIM_THRESHOLD


# ── D3 RAG 召回 Jaccard ──

def _recall(query, *shas):
    return {query: {"context": "", "hits": [{"content_sha256": s, "metadata": {}, "score": 0.5} for s in shas]}}


def test_d3_identical_pass():
    rc = _recall("q1", "h1", "h2", "h3")
    r = gb._diff_d3(rc, rc)
    assert r["degraded"] is False
    assert r["min_jaccard"] == 1.0


def test_d3_hit_shrink_fail():
    g = _recall("q1", "h1", "h2", "h3", "h4")
    c = _recall("q1", "h1", "h2")  # 命中縮減
    r = gb._diff_d3(g, c)
    assert r["degraded"] is True


def test_d3_query_missing_fail():
    g = _recall("q1", "h1", "h2")
    c = {}  # query 缺漏
    r = gb._diff_d3(g, c)
    assert r["degraded"] is True


def test_d3_low_overlap_fail():
    g = _recall("q1", "h1", "h2", "h3", "h4")
    c = _recall("q1", "h1", "x2", "x3", "x4")  # 僅 1/7 重疊 < 0.90
    r = gb._diff_d3(g, c)
    assert r["degraded"] is True
    assert r["min_jaccard"] < gb._D3_JACCARD_THRESHOLD


# ── 紅綠燈裁決彙總 ──

def test_verdict_all_pass_green():
    ok = {"degraded": False}
    assert gb._aggregate_verdict(ok, ok, ok, improvement=False) == "PASS"


def test_verdict_any_fail_red():
    ok, bad = {"degraded": False}, {"degraded": True}
    assert gb._aggregate_verdict(ok, bad, ok, improvement=False) == "FAIL"


def test_verdict_fail_with_improvement_pending_review():
    ok, bad = {"degraded": False}, {"degraded": True}
    assert gb._aggregate_verdict(bad, ok, ok, improvement=True) == "IMPROVEMENT_PENDING_REVIEW"


# ── manifest checksum 防竄改 ──

def test_verify_manifest_tamper_detected(tmp_path):
    f = tmp_path / "D1_zh.md"
    f.write_text("original", encoding="utf-8")
    manifest = {"checksums": {"D1_zh.md": hashlib.sha256(b"original").hexdigest()}}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    # 未竄改 → 通過
    gb._verify_manifest(tmp_path)
    # 竄改後 → 拒絕
    f.write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="竄改"):
        gb._verify_manifest(tmp_path)


def test_diff_one_missing_golden_fail_fast(tmp_path, monkeypatch):
    monkeypatch.setattr(gb, "_GOLDEN_DIR", tmp_path / "nonexistent")
    with pytest.raises(FileNotFoundError, match="capture"):
        gb._diff_one("academic", tmp_path, improvement=False, ts="t")

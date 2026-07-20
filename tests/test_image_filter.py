# === [IMG-FILTER C1] ===
"""image_filter 單元測試（IMG-FILTER C1）。

覆蓋 plan v2 §2.1 規格：stdlib PNG/JPEG header 尺寸解碼／規則①面積（含 481×369 級 KEEP
守門與門檻邊界）／規則②長寬比／規則③報頭比對／任一命中即 DROP／fail-open 容錯／
enabled=False 回 None／DROP 審計 log（caplog）。零第三方影像依賴。
"""

import logging
import struct

import pytest

import settings
from pipelines import image_filter as imf


# ─────────────────── 測試圖檔構造（header-only、_read_image_size 僅讀 header）───────────────────


def _make_png(path, w, h):
    ihdr = struct.pack(">II", w, h) + b"\x08\x02\x00\x00\x00"
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + ihdr + b"\x00" * 8
    )


def _make_jpeg(path, w, h):
    # SOI + APP0（16 bytes 段）+ SOF0（含 h,w）+ 收尾
    app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 9
    sof0 = b"\xff\xc0" + struct.pack(">H", 11) + b"\x08" + struct.pack(">HH", h, w) + b"\x03"
    path.write_bytes(b"\xff\xd8" + app0 + sof0 + b"\xff\xd9")


def _make_jpeg_no_sof(path):
    # SOI + APP0 + 直接 SOS（無 SOF）→ 解析須終止回 None（防無效遍歷）
    app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 9
    path.write_bytes(b"\xff\xd8" + app0 + b"\xff\xda" + b"\x00" * 50)


def _mk(tmp_path, name, w=None, h=None, kind="png", raw=None):
    p = tmp_path / name
    if raw is not None:
        p.write_bytes(raw)
    elif kind == "png":
        _make_png(p, w, h)
    else:
        _make_jpeg(p, w, h)
    return p


def _filter(tmp_path, header_srcs=(), **kw):
    kw.setdefault("min_area", 100_000)
    kw.setdefault("max_aspect", 4.0)
    kw.setdefault("enabled", True)
    return imf.make_figure_filter(tmp_path, header_srcs, **kw)


# ─────────────────── 尺寸解碼（雙格式）───────────────────


class TestReadImageSize:
    def test_png_size(self, tmp_path):
        p = _mk(tmp_path, "a.png", 481, 369, "png")
        assert imf._read_image_size(p) == (481, 369)

    def test_jpeg_size(self, tmp_path):
        p = _mk(tmp_path, "b.jpg", 1575, 852, "jpeg")
        assert imf._read_image_size(p) == (1575, 852)

    def test_jpeg_no_sof_terminates(self, tmp_path):
        """遇 SOS 終止、不做無效遍歷 → 回 None（fail-open 由呼叫端接手）。"""
        p = tmp_path / "c.jpg"
        _make_jpeg_no_sof(p)
        assert imf._read_image_size(p) is None

    def test_unknown_format_none(self, tmp_path):
        p = _mk(tmp_path, "d.bin", raw=b"GIF89a" + b"\x00" * 30)
        assert imf._read_image_size(p) is None


# ─────────────────── 三規則判定 ───────────────────


class TestRules:
    def test_rule1_area_drop_and_keep_guard(self, tmp_path):
        """規則①：147×96（14k）DROP；**481×369（177k）KEEP＝門檻校正守門**。"""
        _mk(tmp_path, "junk.jpg", 147, 96, "jpeg")
        _mk(tmp_path, "chart.jpg", 481, 369, "jpeg")
        f = _filter(tmp_path)
        assert f("images/junk.jpg") is False
        assert f("images/chart.jpg") is True     # spec 原門檻會誤殺、plan 校正後必 KEEP

    def test_rule1_boundary_equal_keeps(self, tmp_path):
        """門檻邊界：area == min_area → KEEP（嚴格小於才 DROP）。"""
        _mk(tmp_path, "edge.png", 400, 250, "png")      # 100,000 整
        assert _filter(tmp_path)("images/edge.png") is True

    def test_rule2_aspect(self, tmp_path):
        """規則②：525×96（5.47）DROP；1575×852（1.85）KEEP；邊界 == 4.0 KEEP。"""
        _mk(tmp_path, "banner.jpg", 525, 96, "jpeg")     # 面積 50k 也中①、此處驗②訊息
        _mk(tmp_path, "wide.png", 2000, 500, "png")      # aspect 恰 4.0、面積 1M
        _mk(tmp_path, "photo.jpg", 1575, 852, "jpeg")
        f = _filter(tmp_path)
        assert f("images/banner.jpg") is False
        assert f("images/wide.png") is True              # == max_aspect 不 DROP
        assert f("images/photo.jpg") is True

    def test_rule2_pure_aspect_hit(self, tmp_path):
        """純規則②命中（面積夠大、比例極端）。"""
        _mk(tmp_path, "strip.png", 3000, 300, "png")     # 面積 900k > 門檻、aspect 10
        assert _filter(tmp_path)("images/strip.png") is False

    def test_rule3_header_srcs(self, tmp_path):
        """規則③：src ∈ header_srcs → DROP（不需讀檔）；∉ → 走①②。"""
        _mk(tmp_path, "big.png", 1500, 1000, "png")
        f = _filter(tmp_path, header_srcs={"images/big.png"})
        assert f("images/big.png") is False              # 大圖但在報頭區 → ③ DROP
        f2 = _filter(tmp_path, header_srcs={"images/other.png"})
        assert f2("images/big.png") is True

    def test_any_rule_hit_drops(self, tmp_path):
        """任一命中即 DROP：三張分別由①②③攔下。"""
        _mk(tmp_path, "tiny.png", 150, 88, "png")
        _mk(tmp_path, "strip.png", 3000, 300, "png")
        _mk(tmp_path, "hdr.png", 1500, 1000, "png")
        f = _filter(tmp_path, header_srcs={"images/hdr.png"})
        assert f("images/tiny.png") is False
        assert f("images/strip.png") is False
        assert f("images/hdr.png") is False


# ─────────────────── fail-open 容錯 ───────────────────


class TestFailOpen:
    def test_missing_file_keeps(self, tmp_path, caplog):
        with caplog.at_level(logging.WARNING):
            assert _filter(tmp_path)("images/nope.jpg") is True
        assert "fail-open" in caplog.text

    def test_garbage_bytes_keeps(self, tmp_path, caplog):
        _mk(tmp_path, "bad.jpg", raw=b"\x00\x01\x02garbage")
        with caplog.at_level(logging.WARNING):
            assert _filter(tmp_path)("images/bad.jpg") is True
        assert "fail-open" in caplog.text

    def test_unknown_format_keeps(self, tmp_path):
        _mk(tmp_path, "e.gif", raw=b"GIF89a" + b"\x00" * 30)
        assert _filter(tmp_path)("images/e.gif") is True


# ─────────────────── 總開關與審計 log ───────────────────


class TestSwitchAndAudit:
    def test_enabled_false_returns_none(self, tmp_path):
        assert imf.make_figure_filter(tmp_path, (), enabled=False) is None

    def test_enabled_default_reads_settings(self, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "IMG_FILTER_ENABLED", False)
        assert imf.make_figure_filter(tmp_path, ()) is None
        monkeypatch.setattr(settings, "IMG_FILTER_ENABLED", True)
        assert imf.make_figure_filter(tmp_path, ()) is not None

    def test_drop_audit_log_contains_src_size_rule(self, tmp_path, caplog):
        """DROP 審計：log 含 src＋實測尺寸＋命中規則（不靜默丟）。"""
        _mk(tmp_path, "junk.jpg", 147, 96, "jpeg")
        _mk(tmp_path, "strip.png", 3000, 300, "png")
        f = _filter(tmp_path, header_srcs={"images/hdr.png"})
        with caplog.at_level(logging.INFO):
            f("images/junk.jpg")
            f("images/strip.png")
            f("images/hdr.png")
        assert "規則①面積" in caplog.text and "images/junk.jpg" in caplog.text \
            and "147x96" in caplog.text
        assert "規則②長寬比" in caplog.text and "3000x300" in caplog.text
        assert "規則③報頭區" in caplog.text and "images/hdr.png" in caplog.text

    def test_keep_is_silent_info(self, tmp_path, caplog):
        _mk(tmp_path, "photo.jpg", 1575, 852, "jpeg")
        with caplog.at_level(logging.INFO):
            assert _filter(tmp_path)("images/photo.jpg") is True
        assert "DROP" not in caplog.text
# === [IMG-FILTER C1 END] ===

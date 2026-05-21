"""Phase 4.7d RAG-7a：md_cleaner 浮水印 heading 偵測 + 移除測試。"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from processor.md_cleaner import MarkdownCleaner  # noqa: E402


@pytest.fixture
def cleaner():
    return MarkdownCleaner()


@pytest.fixture
def tmp_md(tmp_path):
    """建臨時 .md、回傳 helper write(content) -> Path。"""
    p = tmp_path / "test.md"

    def write(content):
        p.write_text(content, encoding='utf-8')
        return p
    return write


def test_existing_numeric_line_removed(cleaner, tmp_md):
    """既有邏輯回歸：純數字行被移除。"""
    p = tmp_md("# Title\n- 8 6 1 8 11 1 2 2 4\n## Section\n")
    cleaner.clean(p)
    content = p.read_text()
    assert "- 8 6 1" not in content
    assert "# Title" in content
    assert "## Section" in content


def test_watermark_heading_removed_threshold_3(cleaner, tmp_md):
    """3 次 # X → 移除；1 / 2 次保留。"""
    p = tmp_md(
        "# XDeHunt\n"
        "## Section A\n"
        "# XDeHunt\n"
        "## Section B\n"
        "# XDeHunt\n"          # 3 次出現 → 視為浮水印
        "## Only Once\n"        # 1 次 → 保留
        "## Only Twice\n"
        "## Only Twice\n"      # 2 次 → 保留
    )
    cleaner.clean(p)
    content = p.read_text()
    assert "XDeHunt" not in content
    assert "## Section A" in content
    assert "## Section B" in content
    assert "## Only Once" in content
    assert content.count("## Only Twice") == 2


def test_watermark_case_insensitive(cleaner, tmp_md):
    """大小寫變體算同一個浮水印。"""
    p = tmp_md(
        "# XDeHunt\n"
        "## A\n"
        "# xdehunt\n"
        "## B\n"
        "# XDEHUNT\n"
    )
    cleaner.clean(p)
    content = p.read_text()
    assert "XDeHunt" not in content
    assert "xdehunt" not in content
    assert "XDEHUNT" not in content
    assert "## A" in content
    assert "## B" in content


def test_watermark_different_hash_count_same(cleaner, tmp_md):
    """# X / ### X / ## X normalize 後算同一個。"""
    p = tmp_md(
        "# X\n"
        "## paragraph A\n"
        "### X\n"
        "## paragraph B\n"
        "## X\n"
    )
    cleaner.clean(p)
    content = p.read_text()
    # 三種變體均被移除（normalize 後同名、總出現 3 次）
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('#'):
            norm = stripped.lstrip('#').strip().casefold()
            assert norm != 'x', f"浮水印行未被移除: {line!r}"
    # 非浮水印保留
    assert "## paragraph A" in content
    assert "## paragraph B" in content


def test_normal_heading_not_removed(cleaner, tmp_md):
    """正常單次 heading 保留（履歷常見結構）。"""
    p = tmp_md(
        "# Paper Title\n"
        "## Working Experience\n"
        "### VIEWTRIX\n"
        "## Education\n"
        "### MIT\n"
    )
    cleaner.clean(p)
    content = p.read_text()
    assert "# Paper Title" in content
    assert "## Working Experience" in content
    assert "### VIEWTRIX" in content
    assert "## Education" in content
    assert "### MIT" in content


def test_threshold_env_override(cleaner, tmp_md, monkeypatch):
    """env WATERMARK_HEADING_THRESHOLD=2 生效——2 次也視為浮水印。"""
    monkeypatch.setenv("WATERMARK_HEADING_THRESHOLD", "2")
    import importlib
    import settings as _settings
    importlib.reload(_settings)
    try:
        p = tmp_md(
            "# Watermark\n"
            "## Section A\n"
            "# Watermark\n"   # 2 次 → 觸發（N=2）
        )
        cleaner.clean(p)
        content = p.read_text()
        assert "Watermark" not in content
        assert "## Section A" in content
    finally:
        # restore default
        monkeypatch.delenv("WATERMARK_HEADING_THRESHOLD")
        importlib.reload(_settings)

"""Phase 4.7e v2 — ResumeProcessor 單元測試（mock LLM、不打 API）。

vs 舊 7e-1 11 個測試：
- 移除 `test_validate_no_working_experience_warns`（v2 鬆綁、不再強制 Working Experience）
- 新增 `test_validate_resume_title_blacklist_exact_raises`
- 新增 `test_validate_resume_title_recomposed_warns`
- 新增 `test_validate_resume_title_real_name_passes`
- 共 14 個
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import fitz  # noqa: E402

from processor.resume_processor import ResumeProcessor  # noqa: E402
from processor.pdf_parser import PDFParseError  # noqa: E402


# 合法人名輸出（用於正向測試）
VALID_OUTPUT = (
    "# Tzung-Yuan Lee (李宗原)\n\n"
    "## Candidate Summary\n\n候選人摘要 prose。\n\n"
    "## Working Experience\n\n"
    "### ACME Inc. - CTO (2020/01 - PRESENT)\n\n職責內容。\n\n"
    "## Technical Skills\n\n- Python\n- Verilog\n"
)


@pytest.fixture
def fake_pdf(tmp_path):
    """產生最小合法 PDF（PyMuPDF 寫 2 頁空白頁）。"""
    pdf_path = tmp_path / "fake_resume.pdf"
    doc = fitz.open()
    for _ in range(2):
        doc.new_page(width=595, height=842)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def mock_llm():
    """Mock LLMClient、chat_with_images 預設回合法 markdown。"""
    m = MagicMock()
    m.chat_with_images.return_value = VALID_OUTPUT
    return m


def test_parse_creates_md_file(fake_pdf, tmp_path, mock_llm):
    """parse() 寫出 .md，內容為 mock LLM 回傳值。"""
    out_dir = tmp_path / "out"
    proc = ResumeProcessor(llm=mock_llm)
    md_path = proc.parse(str(fake_pdf), str(out_dir))

    assert md_path.exists()
    assert md_path.name == "fake_resume.md"
    content = md_path.read_text(encoding="utf-8")
    assert content.startswith("# Tzung-Yuan Lee")
    assert mock_llm.chat_with_images.call_count == 1


def test_parse_creates_page_images(fake_pdf, tmp_path, mock_llm):
    """side product：每頁產生 images/page_NN.jpg。"""
    out_dir = tmp_path / "out"
    proc = ResumeProcessor(llm=mock_llm)
    proc.parse(str(fake_pdf), str(out_dir))

    images_dir = out_dir / "images"
    assert images_dir.is_dir()
    pages = sorted(images_dir.glob("page_*.jpg"))
    assert len(pages) == 2
    assert pages[0].name == "page_01.jpg"
    assert pages[1].name == "page_02.jpg"
    assert pages[0].read_bytes()[:3] == b"\xff\xd8\xff"  # JPEG magic


def test_render_dpi_correct(fake_pdf, tmp_path, mock_llm):
    """確認預設 RENDER_MATRIX = 2.5。"""
    from processor.resume_processor import RENDER_MATRIX
    assert RENDER_MATRIX.a == 2.5 and RENDER_MATRIX.d == 2.5

    proc = ResumeProcessor(llm=mock_llm)
    proc.parse(str(fake_pdf), str(tmp_path / "out"))
    img = (tmp_path / "out" / "images" / "page_01.jpg").read_bytes()
    assert len(img) > 0


def test_vision_call_passes_images_and_model(fake_pdf, tmp_path, mock_llm, monkeypatch):
    """chat_with_images 收到正確張數 + 用 LLM_VISION_MODEL。"""
    import settings
    monkeypatch.setattr(settings, "LLM_VISION_MODEL", "fake-vision-model")
    proc = ResumeProcessor(llm=mock_llm)
    proc.parse(str(fake_pdf), str(tmp_path / "out"))

    args, kwargs = mock_llm.chat_with_images.call_args
    images = kwargs.get("images") or args[1]
    assert len(images) == 2
    for img_bytes, mime in images:
        assert isinstance(img_bytes, bytes)
        assert mime == "image/jpeg"
    assert kwargs.get("model") == "fake-vision-model"


def test_strip_code_fence_markdown(fake_pdf, tmp_path, mock_llm):
    """Vision 回 ```markdown\\n#...\\n``` → strip code fence。"""
    mock_llm.chat_with_images.return_value = (
        "```markdown\n" + VALID_OUTPUT + "\n```"
    )
    proc = ResumeProcessor(llm=mock_llm)
    md_path = proc.parse(str(fake_pdf), str(tmp_path / "out"))
    content = md_path.read_text(encoding="utf-8")
    assert content.startswith("# Tzung-Yuan Lee")
    assert not content.startswith("```")
    assert "```" not in content.splitlines()[-1]


def test_strip_code_fence_plain(fake_pdf, tmp_path, mock_llm):
    """Vision 回 ```\\n#...\\n``` → strip code fence。"""
    mock_llm.chat_with_images.return_value = "```\n" + VALID_OUTPUT + "\n```"
    proc = ResumeProcessor(llm=mock_llm)
    md_path = proc.parse(str(fake_pdf), str(tmp_path / "out"))
    content = md_path.read_text(encoding="utf-8")
    assert content.startswith("# Tzung-Yuan Lee")
    assert not content.startswith("```")


def test_remove_preamble_en(fake_pdf, tmp_path, mock_llm, caplog):
    """'Here is the parsed resume:\\n\\n# Title' → 移 preamble。"""
    import logging
    mock_llm.chat_with_images.return_value = (
        "Here is the parsed resume:\n\n" + VALID_OUTPUT
    )
    proc = ResumeProcessor(llm=mock_llm)
    with caplog.at_level(logging.WARNING):
        md_path = proc.parse(str(fake_pdf), str(tmp_path / "out"))
    content = md_path.read_text(encoding="utf-8")
    assert content.startswith("# Tzung-Yuan Lee")
    assert "Here is" not in content
    assert any("preamble" in r.message for r in caplog.records)


def test_remove_preamble_zh(fake_pdf, tmp_path, mock_llm, caplog):
    """'以下是您的履歷整理：\\n\\n# Title' → 移 preamble。"""
    import logging
    mock_llm.chat_with_images.return_value = (
        "以下是您的履歷整理：\n\n" + VALID_OUTPUT
    )
    proc = ResumeProcessor(llm=mock_llm)
    with caplog.at_level(logging.WARNING):
        md_path = proc.parse(str(fake_pdf), str(tmp_path / "out"))
    content = md_path.read_text(encoding="utf-8")
    assert content.startswith("# Tzung-Yuan Lee")
    assert "以下是" not in content
    assert any("preamble" in r.message for r in caplog.records)


def test_validate_no_heading_raises(fake_pdf, tmp_path, mock_llm):
    """非 # 開頭 + 非 preamble pattern → raise PDFParseError。"""
    mock_llm.chat_with_images.return_value = (
        "This person worked at ACME for 5 years.\nThey know Python.\n"
    )
    proc = ResumeProcessor(llm=mock_llm)
    with pytest.raises(PDFParseError, match="不是 # 開頭"):
        proc.parse(str(fake_pdf), str(tmp_path / "out"))


def test_failure_raises_pdfparseerror(fake_pdf, tmp_path, mock_llm):
    """LLM 拋例外 → 包成 PDFParseError。"""
    mock_llm.chat_with_images.side_effect = RuntimeError("Gemini 5xx")
    proc = ResumeProcessor(llm=mock_llm)
    with pytest.raises(PDFParseError, match="Vision resume parse failed"):
        proc.parse(str(fake_pdf), str(tmp_path / "out"))


def test_large_image_lowers_dpi(tmp_path, mock_llm, monkeypatch, caplog):
    """單頁 render > MAX_PAGE_JPEG_BYTES → fallback Matrix(1.5) + log warning。

    用 monkeypatch 把 MAX_PAGE_JPEG_BYTES 降到極小（10 bytes）、強制觸發 fallback。
    """
    import logging
    import processor.resume_processor as rp
    monkeypatch.setattr(rp, "MAX_PAGE_JPEG_BYTES", 10)

    pdf_path = tmp_path / "big.pdf"
    doc = fitz.open()
    doc.new_page(width=595, height=842)
    doc.save(str(pdf_path))
    doc.close()

    proc = ResumeProcessor(llm=mock_llm)
    with caplog.at_level(logging.WARNING):
        proc.parse(str(pdf_path), str(tmp_path / "out"))

    img_bytes = (tmp_path / "out" / "images" / "page_01.jpg").read_bytes()
    assert len(img_bytes) > 0
    # 驗證 fallback warning 出現
    assert any("降低 dpi 重 render" in r.message for r in caplog.records), \
        "未對超過 MAX_PAGE_JPEG_BYTES 的頁面觸發降 dpi"


# ─────────────────── v2 主標題黑名單測試（3 個新增）───────────────────


def test_validate_resume_title_blacklist_exact_raises(fake_pdf, tmp_path, mock_llm):
    """v2：# Resume / # CV / # 履歷 等黑名單詞 → raise PDFParseError。"""
    blacklisted_titles = [
        "# Resume",
        "# CV",
        "# Curriculum Vitae",
        "# 履歷",
        "# 個人簡歷",
        "# 履歷表",
        "# resume",  # casefold
        "# CURRICULUM VITAE",
    ]
    proc = ResumeProcessor(llm=mock_llm)
    for title in blacklisted_titles:
        mock_llm.chat_with_images.return_value = (
            f"{title}\n\n## Some Section\n\n內容\n"
        )
        with pytest.raises(PDFParseError, match="黑名單通用詞"):
            proc.parse(str(fake_pdf), str(tmp_path / f"out_{hash(title)}"))


def test_validate_resume_title_recomposed_warns(fake_pdf, tmp_path, mock_llm, caplog):
    """v2：# CTO Resume - John Doe 等重組 pattern → warn（不 raise）。"""
    import logging
    recomposed_titles = [
        "# CTO Resume - Tzung-Yuan Lee",
        "# Senior Engineer Resume - 江元杰",
        "# Chinese Language Trainer CV - Priyal Shah",
        "# 行銷部經理 履歷 - 黃忠偉",
    ]
    proc = ResumeProcessor(llm=mock_llm)
    for title in recomposed_titles:
        mock_llm.chat_with_images.return_value = (
            f"{title}\n\n## Working Experience\n\n### ACME - CTO (2020 - PRESENT)\n\n內容\n"
        )
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            md_path = proc.parse(str(fake_pdf), str(tmp_path / f"out_{hash(title)}"))
        # 不 raise、md 寫出
        assert md_path.exists()
        # log warning 有出現
        assert any(
            "重組格式" in r.message for r in caplog.records
        ), f"未對 {title!r} 發 warning"


def test_validate_resume_title_real_name_passes(fake_pdf, tmp_path, mock_llm, caplog):
    """v2：合法人名主標題（人名 / 中文姓名 / 中英並列）→ 通過驗證、無 warning。"""
    import logging
    valid_titles = [
        "# Tzung-Yuan Lee (李宗原)",
        "# 黃忠偉",
        "# Priyal Shah (李思雅)",
        "# 吳焴倫",
        "# 江元杰 (Steven Chiang)",
        "# Chin-Yu Lin 林晉羽",
    ]
    proc = ResumeProcessor(llm=mock_llm)
    for title in valid_titles:
        mock_llm.chat_with_images.return_value = (
            f"{title}\n\n## Education\n\n學校 / 學位\n"
        )
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            md_path = proc.parse(str(fake_pdf), str(tmp_path / f"out_{hash(title)}"))
        # 通過、無黑名單 / 重組 warning
        assert md_path.exists()
        assert not any(
            "黑名單" in r.message or "重組格式" in r.message
            for r in caplog.records
        ), f"合法 title {title!r} 不應觸發黑名單 / 重組 warning"

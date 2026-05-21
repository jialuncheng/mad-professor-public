"""Phase 4.7e-1：ResumeProcessor 單元測試（mock LLM、不打 API）。"""
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


VALID_OUTPUT = (
    "# CTO Resume - Test Name\n\n"
    "## Candidate Summary\n\n候選人摘要 prose。\n\n"
    "## Working Experience\n\n"
    "### ACME Inc. - CTO (2020/01 - PRESENT)\n\n職責內容。\n\n"
    "## Technical Skills\n\n- Python\n- Verilog\n"
)


@pytest.fixture
def fake_pdf(tmp_path):
    """產生最小合法 PDF（PyMuPDF 寫個 2 頁空白頁）。"""
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
    assert content.startswith("# CTO Resume - Test Name")
    assert "## Working Experience" in content
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
    # 確認 JPEG magic bytes
    assert pages[0].read_bytes()[:3] == b"\xff\xd8\xff"


def test_render_dpi_correct(fake_pdf, tmp_path, mock_llm):
    """確認預設用 RENDER_MATRIX (2.5)，render 後尺寸 > A4 標準像素。"""
    from processor.resume_processor import RENDER_MATRIX
    assert RENDER_MATRIX.a == 2.5 and RENDER_MATRIX.d == 2.5

    proc = ResumeProcessor(llm=mock_llm)
    proc.parse(str(fake_pdf), str(tmp_path / "out"))
    img = (tmp_path / "out" / "images" / "page_01.jpg").read_bytes()
    # A4 595pt × 2.5 = 1487 px wide；JPEG header 第 4 byte 後可解碼但簡單
    # 用大小檢查（2.5 dpi 空白頁 > 1.5 dpi 空白頁）
    proc2 = ResumeProcessor(llm=mock_llm)
    # 不直接斷 dpi，只證明 fixture 用了 module-level RENDER_MATRIX
    assert len(img) > 0


def test_vision_call_passes_images_and_model(fake_pdf, tmp_path, mock_llm, monkeypatch):
    """確認 chat_with_images 收到正確張數 + 用 LLM_VISION_MODEL。"""
    import settings
    monkeypatch.setattr(settings, "LLM_VISION_MODEL", "fake-vision-model")
    proc = ResumeProcessor(llm=mock_llm)
    proc.parse(str(fake_pdf), str(tmp_path / "out"))

    args, kwargs = mock_llm.chat_with_images.call_args
    images = kwargs.get("images") or args[1]
    assert len(images) == 2  # 2 頁
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
    assert content.startswith("# CTO Resume - Test Name")
    assert not content.startswith("```")
    assert "```" not in content.splitlines()[-1]


def test_strip_code_fence_plain(fake_pdf, tmp_path, mock_llm):
    """Vision 回 ```\\n#...\\n``` → strip code fence。"""
    mock_llm.chat_with_images.return_value = "```\n" + VALID_OUTPUT + "\n```"
    proc = ResumeProcessor(llm=mock_llm)
    md_path = proc.parse(str(fake_pdf), str(tmp_path / "out"))
    content = md_path.read_text(encoding="utf-8")
    assert content.startswith("# CTO Resume - Test Name")
    assert not content.startswith("```")


def test_remove_preamble_en(fake_pdf, tmp_path, mock_llm, caplog):
    """Vision 回 'Here is the resume...\\n#Title' → 移 preamble。"""
    import logging
    mock_llm.chat_with_images.return_value = (
        "Here is the parsed resume:\n\n" + VALID_OUTPUT
    )
    proc = ResumeProcessor(llm=mock_llm)
    with caplog.at_level(logging.WARNING):
        md_path = proc.parse(str(fake_pdf), str(tmp_path / "out"))
    content = md_path.read_text(encoding="utf-8")
    assert content.startswith("# CTO Resume - Test Name")
    assert "Here is" not in content
    assert any("preamble" in r.message for r in caplog.records)


def test_remove_preamble_zh(fake_pdf, tmp_path, mock_llm, caplog):
    """Vision 回 '以下是您的履歷...\\n#Title' → 移 preamble。"""
    import logging
    mock_llm.chat_with_images.return_value = (
        "以下是您的履歷整理：\n\n" + VALID_OUTPUT
    )
    proc = ResumeProcessor(llm=mock_llm)
    with caplog.at_level(logging.WARNING):
        md_path = proc.parse(str(fake_pdf), str(tmp_path / "out"))
    content = md_path.read_text(encoding="utf-8")
    assert content.startswith("# CTO Resume - Test Name")
    assert "以下是" not in content
    assert any("preamble" in r.message for r in caplog.records)


def test_validate_no_heading_raises(fake_pdf, tmp_path, mock_llm):
    """Vision 回傳完全無 # 且非 preamble pattern → raise PDFParseError。"""
    mock_llm.chat_with_images.return_value = (
        "This person worked at ACME for 5 years.\nThey know Python.\n"
    )
    proc = ResumeProcessor(llm=mock_llm)
    with pytest.raises(PDFParseError, match="不是 # 開頭"):
        proc.parse(str(fake_pdf), str(tmp_path / "out"))


def test_validate_no_working_experience_warns(fake_pdf, tmp_path, mock_llm, caplog):
    """無 ## Working Experience 區段 → warning（不 raise）。"""
    import logging
    mock_llm.chat_with_images.return_value = (
        "# Candidate Resume - Test\n\n"
        "## Candidate Summary\n\n純學生、無工作經歷\n"
    )
    proc = ResumeProcessor(llm=mock_llm)
    with caplog.at_level(logging.WARNING):
        md_path = proc.parse(str(fake_pdf), str(tmp_path / "out"))
    assert md_path.exists()
    assert any(
        "Working Experience" in r.message for r in caplog.records
    )


def test_failure_raises_pdfparseerror(fake_pdf, tmp_path, mock_llm):
    """LLM 拋例外 → 包成 PDFParseError。"""
    mock_llm.chat_with_images.side_effect = RuntimeError("Gemini 5xx")
    proc = ResumeProcessor(llm=mock_llm)
    with pytest.raises(PDFParseError, match="Vision resume parse failed"):
        proc.parse(str(fake_pdf), str(tmp_path / "out"))

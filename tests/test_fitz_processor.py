"""PIPE-INGEST-FITZ C1 — FitzProcessor 單元測試。

fixture 一律以 fitz 程式化生成 born-digital PDF（零網路、零外部解析服務）。
覆蓋：同形 .md 契約（`\n\n` 段落 / `#`/`##` 字級推導）、座標閱讀序、
跨頁重複頁首尾剝除、圖 PNG/JPEG 限定與 `page_{page_idx}_{xref}.{ext}`
命名唯一性、`median_page_chars` 閘門輔助、壞檔 `PDFParseError`。
"""
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from processor.fitz_processor import (  # noqa: E402
    FitzProcessor,
    median_page_chars,
)
from processor.pdf_parser import PDFParseError, PDFParser  # noqa: E402

BODY = 11.0
H1 = 24.0
H2 = 17.0


def _new_pdf(path: Path, builder) -> Path:
    doc = fitz.open()
    builder(doc)
    doc.save(str(path))
    doc.close()
    return path


def _text(page, y, text, size=BODY):
    page.insert_text(fitz.Point(72, y), text, fontsize=size)


def _article_builder(doc):
    """兩頁文章：H1/H2 標題、多段正文、跨頁重複頁首尾（頁碼帶變動數字）。"""
    p1 = doc.new_page()  # 預設 A4：595 x 842
    _text(p1, 30, "https://example.com/article — printed", size=8)   # 頂 band
    _text(p1, 120, "Main Title", size=H1)
    _text(p1, 170, "Section One", size=H2)
    _text(p1, 220, "First paragraph body text.")
    _text(p1, 300, "Second paragraph body text.")
    _text(p1, 830, "Page 1 of 2", size=8)                            # 底 band

    p2 = doc.new_page()
    _text(p2, 30, "https://example.com/article — printed", size=8)
    _text(p2, 120, "Section Two", size=H2)
    _text(p2, 180, "Third paragraph body text.")
    _text(p2, 830, "Page 2 of 2", size=8)


@pytest.fixture()
def article_md(tmp_path):
    pdf = _new_pdf(tmp_path / "article.pdf", _article_builder)
    md_path = FitzProcessor().parse(str(pdf), str(tmp_path / "out"))
    return md_path, md_path.read_text(encoding="utf-8")


class TestAbcContract:
    def test_is_pdfparser_impl(self):
        assert issubclass(FitzProcessor, PDFParser)

    def test_parse_returns_stem_md_under_output_dir(self, article_md):
        md_path, _ = article_md
        assert md_path.name == "article.md"
        assert md_path.parent.name == "out"
        assert md_path.exists()

    def test_missing_pdf_raises_filenotfound(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            FitzProcessor().parse(str(tmp_path / "nope.pdf"), str(tmp_path))

    def test_corrupt_pdf_raises_pdfparse_error(self, tmp_path):
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"this is not a pdf at all")
        with pytest.raises(PDFParseError):
            FitzProcessor().parse(str(bad), str(tmp_path / "out"))


class TestIsomorphicMarkdown:
    def test_headings_by_font_size_clustering(self, article_md):
        _, md = article_md
        lines = md.splitlines()
        assert "# Main Title" in lines          # 最大字級群 → #
        assert "## Section One" in lines        # 次級 → ##
        assert "## Section Two" in lines
        assert not any(l.startswith("# First") for l in lines)  # 正文不加

    def test_paragraphs_separated_by_blank_line(self, article_md):
        _, md = article_md
        blocks = md.strip().split("\n\n")
        assert "First paragraph body text." in blocks
        assert "Second paragraph body text." in blocks  # 各自成段、\n\n 分隔

    def test_reading_order_by_coordinates(self, article_md):
        _, md = article_md
        order = [md.index(s) for s in (
            "# Main Title", "## Section One", "First paragraph",
            "Second paragraph", "## Section Two", "Third paragraph",
        )]
        assert order == sorted(order)

    def test_print_header_footer_stripped(self, article_md):
        _, md = article_md
        assert "example.com/article" not in md   # 頂 band 跨頁重複 URL 戳記
        assert "Page 1 of 2" not in md           # 底 band 頁碼（數字歸一後同形）
        assert "Page 2 of 2" not in md

    def test_body_kept_intact(self, article_md):
        _, md = article_md
        for s in ("First paragraph body text.", "Second paragraph body text.",
                  "Third paragraph body text."):
            assert s in md


class TestImages:
    @staticmethod
    def _image_builder(doc):
        for i in range(2):
            page = doc.new_page()
            _text(page, 100, f"Title {i}", size=H1)
            pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 12, 12))
            pix.clear_with(200)
            page.insert_image(fitz.Rect(72, 200, 172, 300), pixmap=pix)
            _text(page, 400, f"Body paragraph {i} text.")

    def test_images_written_png_jpeg_with_unique_names(self, tmp_path):
        pdf = _new_pdf(tmp_path / "imgs.pdf", self._image_builder)
        md_path = FitzProcessor().parse(str(pdf), str(tmp_path / "out"))
        md = md_path.read_text(encoding="utf-8")

        refs = re.findall(r"!\[\]\(images/(page_\d+_\d+\.(?:png|jpeg|jpg))\)", md)
        assert len(refs) == 2
        assert len(set(refs)) == 2  # page_{page_idx}_{xref} 跨頁唯一、零覆寫
        for fname in refs:
            f = md_path.parent / "images" / fname
            assert f.exists() and f.stat().st_size > 0

    def test_image_in_reading_order_between_text(self, tmp_path):
        pdf = _new_pdf(tmp_path / "imgs.pdf", self._image_builder)
        md = FitzProcessor().parse(str(pdf), str(tmp_path / "out")).read_text(
            encoding="utf-8"
        )
        assert md.index("# Title 0") < md.index("![](images/") < md.index(
            "Body paragraph 0"
        )


class TestNoFileMetadata:
    def test_source_has_zero_fitz_metadata_access(self):
        """AST 掃描代碼層零 `.metadata` 屬性存取（docstring 提及不算；plan §2.4）。"""
        import ast

        src = (Path(__file__).resolve().parent.parent
               / "processor" / "fitz_processor.py").read_text(encoding="utf-8")
        hits = [
            node.lineno
            for node in ast.walk(ast.parse(src))
            if isinstance(node, ast.Attribute) and node.attr == "metadata"
        ]
        assert hits == []  # 零檔案屬性依賴（meta 純正文）


class TestMedianPageChars:
    def test_born_digital_far_above_threshold(self, tmp_path):
        pdf = _new_pdf(tmp_path / "article.pdf", _article_builder)
        assert median_page_chars(str(pdf)) > 30.0

    def test_blank_pages_zero(self, tmp_path):
        def builder(doc):
            doc.new_page()
            doc.new_page()
        pdf = _new_pdf(tmp_path / "blank.pdf", builder)
        assert median_page_chars(str(pdf)) == 0.0

    def test_median_resists_sparse_cover_page(self, tmp_path):
        def builder(doc):
            doc.new_page()  # 空封面
            for i in range(2):
                page = doc.new_page()
                for j in range(6):
                    _text(page, 100 + j * 40, f"Dense body line {i}-{j} " * 4)
        pdf = _new_pdf(tmp_path / "mixed.pdf", builder)
        assert median_page_chars(str(pdf)) > 100.0  # 中位數不被稀疏頁拉垮

    def test_corrupt_file_raises_for_caller_failopen(self, tmp_path):
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"garbage")
        with pytest.raises(Exception):  # 呼叫端（C3 閘門）負責 fail-open
            median_page_chars(str(bad))

"""
tests/test_pdf_optimize.py — Unit tests for utils/pdf_optimizer.py

Tests:
    1. test_optimize_pdf_lossless_success
       — valid PDF is optimized, returns True, no .tmp.pdf residue, result is readable.
    2. test_optimize_pdf_lossless_corrupted_fallback
       — corrupt bytes return False, original file preserved, no exception propagated,
         no .tmp.pdf residue.
"""
import sys
from pathlib import Path

import fitz
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.pdf_optimizer import optimize_pdf_lossless  # noqa: E402


def _make_minimal_pdf(path):
    """Create a minimal 1-page PDF at the given path using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4
    page.insert_text((50, 100), "OPTIMIZE-1 test page", fontsize=12)
    doc.save(str(path))
    doc.close()


class TestOptimizePdfLossless:
    def test_optimize_pdf_lossless_success(self, tmp_path):
        """Lossless optimization of a valid PDF succeeds atomically."""
        pdf_file = tmp_path / "sample.pdf"
        _make_minimal_pdf(pdf_file)
        original_size = pdf_file.stat().st_size
        assert original_size > 0

        result = optimize_pdf_lossless(pdf_file)

        # Returns True on success
        assert result is True
        # Output file still exists
        assert pdf_file.exists()
        # No .tmp.pdf residue left behind
        assert not pdf_file.with_suffix(".tmp.pdf").exists()
        # Result is a readable PDF
        doc = fitz.open(str(pdf_file))
        assert doc.page_count >= 1
        doc.close()

    def test_optimize_pdf_lossless_corrupted_fallback(self, tmp_path):
        """Corrupt input returns False; original bytes preserved; no exception raised."""
        pdf_file = tmp_path / "corrupt.pdf"
        original_content = b"not a valid pdf"
        pdf_file.write_bytes(original_content)

        # Must not raise any exception
        result = optimize_pdf_lossless(pdf_file)

        # Returns False on failure (graceful degradation)
        assert result is False
        # Original file content is untouched
        assert pdf_file.read_bytes() == original_content
        # No .tmp.pdf residue left behind
        assert not pdf_file.with_suffix(".tmp.pdf").exists()

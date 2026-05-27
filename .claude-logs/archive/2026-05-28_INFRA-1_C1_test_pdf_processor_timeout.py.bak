"""
Unit tests for MODEL-10 C1: PDFProcessor MINERU_TIMEOUT defensive loading.

Tests:
  A. Default timeout is 1800 when MINERU_TIMEOUT env not set.
  B. Custom timeout is respected when MINERU_TIMEOUT=600.
  C. Invalid MINERU_TIMEOUT (non-numeric) falls back to 1800 without crashing.
"""

import io
import os
import sys
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from processor.pdf_processor import PDFProcessor  # noqa: E402


def _make_minimal_zip(paper_name: str = "original") -> bytes:
    """Build a minimal ZIP that satisfies pdf_processor's ZIP extraction logic."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(f"{paper_name}/auto/{paper_name}.md", "# test")
    return buf.getvalue()


def _mock_response(zip_bytes: bytes, status: int = 200):
    resp = MagicMock()
    resp.status_code = status
    resp.content = zip_bytes
    resp.headers = {"x-mineru-task-id": "test-task-123"}
    resp.text = ""
    return resp


class TestMineruTimeout:
    """Tests for MINERU_TIMEOUT defensive loading and usage."""

    def test_default_timeout_is_1800(self, tmp_path):
        """
        Case A: When MINERU_TIMEOUT env var is not set,
        requests.post must be called with timeout=1800.
        """
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        zip_bytes = _make_minimal_zip("original")

        # Ensure MINERU_TIMEOUT is absent for this test
        env_without_timeout = {k: v for k, v in os.environ.items() if k != "MINERU_TIMEOUT"}
        with patch.dict("os.environ", env_without_timeout, clear=True):
            proc = PDFProcessor()

            assert proc.MINERU_TIMEOUT == 1800, (
                f"Expected MINERU_TIMEOUT=1800, got {proc.MINERU_TIMEOUT}"
            )

            with patch("requests.post") as mock_post:
                mock_post.return_value = _mock_response(zip_bytes)
                try:
                    proc.process(str(pdf_file), str(tmp_path / "out"))
                except Exception:
                    pass  # We only care that timeout=1800 was passed

                assert mock_post.called, "requests.post should have been called"
                _, call_kwargs = mock_post.call_args
                assert call_kwargs.get("timeout") == 1800, (
                    f"Expected timeout=1800, got {call_kwargs.get('timeout')}"
                )

    def test_custom_timeout_via_env(self, tmp_path):
        """
        Case B: When MINERU_TIMEOUT=600 is set,
        requests.post must be called with timeout=600.
        """
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        zip_bytes = _make_minimal_zip("original")

        with patch.dict("os.environ", {"MINERU_TIMEOUT": "600"}):
            proc = PDFProcessor()

            assert proc.MINERU_TIMEOUT == 600, (
                f"Expected MINERU_TIMEOUT=600, got {proc.MINERU_TIMEOUT}"
            )

            with patch("requests.post") as mock_post:
                mock_post.return_value = _mock_response(zip_bytes)
                try:
                    proc.process(str(pdf_file), str(tmp_path / "out"))
                except Exception:
                    pass

                assert mock_post.called, "requests.post should have been called"
                _, call_kwargs = mock_post.call_args
                assert call_kwargs.get("timeout") == 600, (
                    f"Expected timeout=600, got {call_kwargs.get('timeout')}"
                )

    def test_invalid_env_fallback_to_default(self, tmp_path):
        """
        Case C: When MINERU_TIMEOUT is set to a non-numeric string (e.g. 'abc'),
        the processor must NOT crash and must fall back to the default timeout of 1800.
        """
        with patch.dict("os.environ", {"MINERU_TIMEOUT": "abc"}):
            # Should not raise any exception during __init__
            proc = PDFProcessor()

            assert proc.MINERU_TIMEOUT == 1800, (
                f"Expected fallback MINERU_TIMEOUT=1800, got {proc.MINERU_TIMEOUT}"
            )

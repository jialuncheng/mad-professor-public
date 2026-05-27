"""
utils/pdf_optimizer.py — PDF Lossless Optimization Module

Provides atomic lossless PDF optimization using PyMuPDF (fitz).
Safety pattern: write to <name>.tmp.pdf, then os.replace() for crash-safe atomic overwrite.
Logging SOP compliant: event=performance_metric, stage=pdf_optimize, duration_seconds=float.
"""
import logging
import time
from pathlib import Path

import fitz  # pymupdf

logger = logging.getLogger(__name__)


def optimize_pdf_lossless(pdf_path) -> bool:
    """
    Atomically optimize a PDF file in-place using lossless PyMuPDF compression.

    Safety pattern:
        1. Write optimized content to <name>.tmp.pdf (crash-safe staging)
        2. os.replace() for atomic overwrite — no in-place clobbering

    PyMuPDF save flags:
        garbage=3  — GC dead objects + compact xref + dedup streams + clean xref table
        deflate=True — deflate-compress all streams
        clean=True — sanitize content streams

    Args:
        pdf_path: Path-like or str pointing to the PDF to optimize.

    Returns:
        True  — optimization succeeded; file replaced atomically.
        False — optimization failed; original file retained (graceful degradation).
    """
    pdf_path = Path(pdf_path)
    tmp_path = pdf_path.with_suffix(".tmp.pdf")
    t0 = time.time()
    try:
        original_size = pdf_path.stat().st_size
        doc = fitz.open(str(pdf_path))
        doc.save(str(tmp_path), garbage=3, deflate=True, clean=True)
        doc.close()
        tmp_path.replace(pdf_path)  # atomic overwrite — crash-safe
        optimized_size = pdf_path.stat().st_size
        duration = round(time.time() - t0, 2)
        saved_bytes = original_size - optimized_size
        saved_pct = round(saved_bytes / original_size * 100, 1) if original_size > 0 else 0.0
        logger.info(
            f"PDF losslessly optimized: {pdf_path.name}",
            extra={
                "extra_fields": {
                    "event": "performance_metric",
                    "stage": "pdf_optimize",
                    "file": pdf_path.name,
                    "original_bytes": original_size,
                    "optimized_bytes": optimized_size,
                    "saved_bytes": saved_bytes,
                    "saved_pct": saved_pct,
                    "duration_seconds": duration,
                }
            },
        )
        return True
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)  # clean up partial tmp on failure
        logger.warning(
            f"PDF optimization failed, retaining original: {pdf_path.name}",
            extra={"extra_fields": {"file": pdf_path.name}},
            exc_info=True,
        )
        return False

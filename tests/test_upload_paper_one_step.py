"""
tests/test_upload_paper_one_step.py — Unit tests for OPTIMIZE-1 C2
1-Step Upload endpoint (upload_paper with doc_type Form parameter).

Tests:
    1. test_upload_paper_one_step_processing
       — POST /api/papers/upload with file + doc_type → HTTP 200, status=processing.
    2. test_upload_paper_invalid_doc_type
       — POST with invalid doc_type → HTTP 422 / 400, not processing.
    3. test_upload_paper_non_pdf_extension
       — POST .txt file → HTTP 400 with appropriate error.
"""
import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def minimal_pdf_bytes():
    """Create minimal valid PDF bytes for testing."""
    import fitz
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 100), "OPTIMIZE-1 test", fontsize=12)
    buf = doc.write()
    doc.close()
    return buf


@pytest.fixture
def upload_client(tmp_path, monkeypatch):
    """Build minimal FastAPI test client for upload_paper endpoint.

    Bypasses auth_guard / SessionMiddleware. Patches:
    - OUTPUT_DIR → tmp_path
    - optimize_pdf_lossless → noop (always True)
    - run_pipeline → recorded but not actually executed
    """
    import web_server
    from fastapi import FastAPI, Depends
    from fastapi.testclient import TestClient

    # Redirect OUTPUT_DIR to tmp_path to avoid polluting real storage
    monkeypatch.setattr(web_server, 'OUTPUT_DIR', tmp_path)

    # Stub optimize_pdf_lossless to be a no-op (returns True immediately)
    monkeypatch.setattr(web_server, 'optimize_pdf_lossless', lambda path: True)

    # Capture run_pipeline invocations without running the real pipeline
    pipeline_calls = []

    async def fake_run_pipeline(*args, **kwargs):
        pipeline_calls.append((args, kwargs))

    monkeypatch.setattr(web_server, 'run_pipeline', fake_run_pipeline)

    # Mock current_user dependency
    mock_user = MagicMock()
    mock_user.id = 42

    app = FastAPI()
    app.post("/api/papers/upload")(
        web_server.upload_paper.__wrapped__
        if hasattr(web_server.upload_paper, '__wrapped__')
        else web_server.upload_paper
    )

    # Override get_current_user dependency to return mock_user
    from web_server import get_current_user
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Re-register the endpoint with dependency override
    from fastapi import BackgroundTasks, UploadFile, File
    from fastapi.param_functions import Form as FastAPIForm

    # Build a fresh app with the real upload_paper but mocked dependencies
    app2 = FastAPI()
    app2.dependency_overrides[get_current_user] = lambda: mock_user

    @app2.post("/api/papers/upload")
    async def _upload(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        doc_type: str = FastAPIForm(...),
        current_user=Depends(get_current_user),
    ):
        return await web_server.upload_paper(
            background_tasks=background_tasks,
            file=file,
            doc_type=doc_type,
            current_user=current_user,
        )

    client = TestClient(app2, raise_server_exceptions=True)
    return client, pipeline_calls


class TestUploadPaperOneStep:

    def test_upload_paper_one_step_processing(self, upload_client, minimal_pdf_bytes):
        """One-step upload with valid PDF + doc_type returns 200 and status=processing."""
        client, pipeline_calls = upload_client
        response = client.post(
            "/api/papers/upload",
            files={"file": ("thesis.pdf", minimal_pdf_bytes, "application/pdf")},
            data={"doc_type": "academic"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["status"] == "processing"
        assert "paper_id" in data

    def test_upload_paper_invalid_doc_type(self, upload_client, minimal_pdf_bytes):
        """POST with unknown doc_type returns 4xx — not processing."""
        client, _ = upload_client
        response = client.post(
            "/api/papers/upload",
            files={"file": ("thesis.pdf", minimal_pdf_bytes, "application/pdf")},
            data={"doc_type": "unknown_type"},
        )
        assert response.status_code in (400, 422), response.text

    def test_upload_paper_non_pdf_extension(self, upload_client):
        """POST .txt file returns 400."""
        client, _ = upload_client
        response = client.post(
            "/api/papers/upload",
            files={"file": ("report.txt", b"some text", "text/plain")},
            data={"doc_type": "academic"},
        )
        assert response.status_code == 400, response.text

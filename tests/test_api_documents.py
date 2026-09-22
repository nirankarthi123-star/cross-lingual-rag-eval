import io
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from backend.main import app
from backend.config.settings import get_settings

client = TestClient(app)


def test_document_upload_success(tmp_path, monkeypatch):
    """Test successful upload of a .txt file."""
    settings = get_settings()
    original_dir = settings.DOCUMENTS_DIR
    # Point DOCUMENTS_DIR at tmp_path for isolation
    monkeypatch.setattr(settings, "DOCUMENTS_DIR", str(tmp_path / "documents"))

    file_content = b"This is a test document for upload."
    files = {"file": ("test_doc.txt", io.BytesIO(file_content), "text/plain")}
    data = {"source_url": "http://example.com/test_doc.txt"}

    response = client.post("/api/documents/upload", files=files, data=data)

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert "filename" in res_data
    assert "test_doc.txt" in res_data["filename"]

    # Verify the file was actually saved
    docs_dir = tmp_path / "documents"
    assert docs_dir.exists()
    saved_files = list(docs_dir.glob("*_test_doc.txt"))
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == file_content

    # Restore
    monkeypatch.setattr(settings, "DOCUMENTS_DIR", original_dir)


def test_document_upload_invalid_extension(tmp_path, monkeypatch):
    """Test that unsupported extensions are rejected."""
    settings = get_settings()
    monkeypatch.setattr(settings, "DOCUMENTS_DIR", str(tmp_path / "documents"))

    file_content = b"Binary data"
    files = {"file": ("malware.exe", io.BytesIO(file_content), "application/octet-stream")}
    data = {"source_url": "http://example.com/malware.exe"}

    response = client.post("/api/documents/upload", files=files, data=data)

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_document_upload_pdf(tmp_path, monkeypatch):
    """Test that .pdf extension is accepted."""
    settings = get_settings()
    monkeypatch.setattr(settings, "DOCUMENTS_DIR", str(tmp_path / "documents"))

    file_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("report.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"source_url": "https://example.com/report.pdf"}

    response = client.post("/api/documents/upload", files=files, data=data)

    assert response.status_code == 200
    assert response.json()["status"] == "success"

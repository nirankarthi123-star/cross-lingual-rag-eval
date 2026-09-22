from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    """Verify that GET /health returns HTTP 200 and {'status': 'ok'}."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_document_stats_endpoint():
    """Verify that GET /api/documents/stats returns valid dataset metrics."""
    response = client.get("/api/documents/stats")
    assert response.status_code == 200
    data = response.json()
    assert "num_documents" in data
    assert "num_chunks" in data
    assert data["num_documents"] >= 0
    assert data["num_chunks"] >= 0


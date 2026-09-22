"""
Tests verifying that page routes return HTML and API routes return JSON.
"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_returns_chatbot_html():
    """GET / must serve the chatbot HTML page, not JSON."""
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    # Must contain the chatbot page title or key landmark
    assert b"RAG Chatbot" in r.content or b"chat" in r.content.lower()


def test_documents_route_returns_html():
    """GET /documents must serve the documents HTML page, not JSON."""
    r = client.get("/documents")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert b"html" in r.content.lower()


def test_dashboard_route_returns_html():
    """GET /dashboard must serve the evaluation dashboard HTML page, not JSON."""
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert b"html" in r.content.lower()


def test_api_chat_is_not_html():
    """POST /api/chat must return JSON, not HTML."""
    r = client.post("/api/chat", json={"query": "test", "mitigation_enabled": False})
    # Could be 200 or 500 (service not init in test), but must not be HTML
    assert "application/json" in r.headers["content-type"]


def test_api_dashboard_summary_is_json():
    """GET /api/dashboard/summary must return JSON."""
    r = client.get("/api/dashboard/summary")
    assert r.status_code == 200
    assert "application/json" in r.headers["content-type"]
    data = r.json()
    # Must be a dict (summary object), not an HTML string
    assert isinstance(data, dict)


def test_api_documents_stats_is_json():
    """GET /api/documents/stats must return JSON."""
    r = client.get("/api/documents/stats")
    assert r.status_code == 200
    assert "application/json" in r.headers["content-type"]
    data = r.json()
    assert isinstance(data, dict)


def test_page_routes_never_return_json():
    """Sanity check: none of the three page URLs return content-type JSON."""
    for path in ["/", "/documents", "/dashboard"]:
        r = client.get(path)
        assert "application/json" not in r.headers.get("content-type", ""), (
            f"{path} returned JSON content-type, expected HTML"
        )

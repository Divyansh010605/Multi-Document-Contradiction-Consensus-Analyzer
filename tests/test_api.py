"""API tests for FastAPI endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_endpoint_runs() -> None:
    payload = {
        "documents": [
            {"source": "A", "text": "The policy reduces emissions by 20 percent."},
            {"source": "B", "text": "The policy does not reduce emissions by 20 percent."},
            {"source": "C", "text": "Independent review says the policy reduces emissions."},
        ]
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "claims" in data
    assert "stats" in data
    assert data["stats"]["document_count"] == 3

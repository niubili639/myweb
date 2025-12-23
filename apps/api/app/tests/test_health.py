from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_status():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert "status" in payload
    assert payload["status"] == "ok"
    assert "data" in payload
    assert "service" in payload["data"]

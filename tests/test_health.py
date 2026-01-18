from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch

client = TestClient(app)

@patch("db.db.check_mongodb_health", new_callable=AsyncMock)
def test_health_check_ok(mock_health):
    mock_health.return_value = True
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["api_status"] == "ok"
    assert data["mongodb_status"] == "ok"
    assert "version" in data
    assert "timestamp" in data

@patch("db.db.check_mongodb_health", new_callable=AsyncMock)
def test_health_check_unavailable(mock_health):
    mock_health.return_value = False
    response = client.get("/health")
    assert response.status_code == 503
    data = response.json()
    assert data["api_status"] == "ok"
    assert data["mongodb_status"] == "unavailable" 

from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch

client = TestClient(app)

@patch("db.db.check_mongodb_health", new_callable=AsyncMock)
def test_health_check(mock_health):
    mock_health.return_value = True
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Service is healthy"}

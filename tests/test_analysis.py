from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_analysis_perform():
    # Mock logic would go here if we were hitting DB
    payload = {
        "dataset_id": "123",
        "analysis_type": "summary"
    }
    # Currently analysis endpoint mocks internal logic so this should pass
    response = client.post("/analysis/perform", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_id"] == "123"
    assert "result_data" in data

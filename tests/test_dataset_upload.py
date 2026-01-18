from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("services.cloudinary_service.CloudinaryService.upload_file")
def test_dataset_upload(mock_upload):
    # Mock successful upload
    mock_upload.return_value = {"url": "http://test.com/file.csv", "public_id": "123"}
    
    csv_content = "col1,col2\nval1,val2"
    files = {"file": ("test.csv", csv_content, "text/csv")}
    
    response = client.post("/datasets/upload", files=files)
    
    assert response.status_code == 201
    assert response.json()["message"] == "File uploaded successfully"
    assert response.json()["url"] == "http://test.com/file.csv"

def test_dataset_upload_invalid_extension():
    files = {"file": ("test.txt", "content", "text/plain")}
    response = client.post("/datasets/upload", files=files)
    assert response.status_code == 400

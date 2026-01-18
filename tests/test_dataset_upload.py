from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_dataset_upload_as_analyst_success(
    analyst_token,
    mock_authz_user_lookup,
    mock_cloudinary,
    mock_datasets_collection,
    mock_analysis_logger,
):
    files = {"file": ("test.csv", "city,region,sites\nA,R1,5\nB,R1,7", "text/csv")}
    response = client.post(
        "/datasets/upload",
        files=files,
        data={"analysis_type": "galamsay", "params": "{\"threshold\": 5}"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["message"].startswith("File uploaded")
    assert "dataset_id" in body
    assert "analysis_id" in body
    assert "analysis" in body


def test_dataset_upload_viewer_forbidden(
    viewer_token,
    mock_authz_user_lookup,
    mock_cloudinary,
):
    files = {"file": ("test.csv", "a,b\n1,2", "text/csv")}
    response = client.post(
        "/datasets/upload",
        files=files,
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert response.status_code == 403


def test_dataset_upload_unauthenticated(mock_cloudinary):
    files = {"file": ("test.csv", "a,b\n1,2", "text/csv")}
    response = client.post("/datasets/upload", files=files)
    assert response.status_code == 401


def test_dataset_upload_invalid_extension(
    analyst_token, mock_authz_user_lookup, mock_cloudinary
):
    files = {"file": ("test.txt", "content", "text/plain")}
    response = client.post(
        "/datasets/upload",
        files=files,
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 400

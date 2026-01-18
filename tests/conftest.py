import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock
from dependencies.authh import create_access_token, get_password_hash
from bson import ObjectId


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def analyst_user_id() -> str:
    return str(ObjectId())


@pytest.fixture()
def viewer_user_id() -> str:
    return str(ObjectId())


@pytest.fixture()
def analyst_token(analyst_user_id: str) -> str:
    return create_access_token(subject=analyst_user_id)


@pytest.fixture()
def viewer_token(viewer_user_id: str) -> str:
    return create_access_token(subject=viewer_user_id)


@pytest.fixture()
def mock_authz_user_lookup(monkeypatch, analyst_user_id: str, viewer_user_id: str):
    async def _find_one(filter=None, *args, **kwargs):
        # Return an analyst or viewer based on filter provided ObjectId
        obj_id = filter.get("_id") if filter else None
        if isinstance(obj_id, ObjectId) and str(obj_id) == analyst_user_id:
            return {"_id": ObjectId(analyst_user_id), "email": "analyst@example.com", "role": "analyst", "password": get_password_hash("Password123!")}
        if isinstance(obj_id, ObjectId) and str(obj_id) == viewer_user_id:
            return {"_id": ObjectId(viewer_user_id), "email": "viewer@example.com", "role": "viewer", "password": get_password_hash("Password123!")}
        return None

    monkeypatch.setattr("dependencies.authz.users_collection.find_one", _find_one)


@pytest.fixture()
def mock_cloudinary(monkeypatch):
    def _upload_file(file, folder: str = "ofwa_dash"):
        return {"url": "https://res.cloudinary.com/demo/raw/upload/v1/test.csv", "public_id": "raw/test.csv"}
    monkeypatch.setattr("services.cloudinary_service.CloudinaryService.upload_file", staticmethod(_upload_file))


@pytest.fixture()
def mock_datasets_collection(monkeypatch):
    class _InsertResult:
        def __init__(self, inserted_id):
            self.inserted_id = inserted_id

    async def _insert_one(doc):
        return _InsertResult(ObjectId())

    monkeypatch.setattr("routes.datasets.datasets_collection.insert_one", _insert_one)


@pytest.fixture()
def mock_analysis_logger(monkeypatch):
    async def _success(**kwargs):
        return "analysis-log-id"

    async def _failure(**kwargs):
        return "analysis-log-id"

    monkeypatch.setattr("services.analysis_logger.analysis_logger.log_success", _success)
    monkeypatch.setattr("services.analysis_logger.analysis_logger.log_failure", _failure)

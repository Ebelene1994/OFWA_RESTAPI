from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock
from dependencies.authh import get_password_hash

client = TestClient(app)


def test_register_user_success(monkeypatch):
    async def _count_documents(filter=None, *args, **kwargs):
        return 0

    class _InsertResult:
        def __init__(self, inserted_id):
            self.inserted_id = "user_id"

    async def _insert_one(doc):
        return _InsertResult("user_id")

    monkeypatch.setattr("routes.users.users_collection.count_documents", _count_documents)
    monkeypatch.setattr("routes.users.users_collection.insert_one", _insert_one)

    resp = client.post(
        "/users/register",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123!",
            "role": "viewer",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["message"].startswith("User registered successfully")


def test_register_user_conflict(monkeypatch):
    async def _count_documents(filter=None, *args, **kwargs):
        return 1

    monkeypatch.setattr("routes.users.users_collection.count_documents", _count_documents)

    resp = client.post(
        "/users/register",
        data={
            "username": "bob",
            "email": "bob@example.com",
            "password": "Password123!",
            "role": "viewer",
        },
    )
    assert resp.status_code == 409


def test_login_user_success(monkeypatch):
    hashed = get_password_hash("Password123!")

    async def _find_one(filter=None, *args, **kwargs):
        return {
            "_id": "user_id",
            "email": "carol@example.com",
            "password": hashed,
            "role": "analyst",
        }

    monkeypatch.setattr("routes.users.users_collection.find_one", _find_one)

    resp = client.post(
        "/users/login",
        data={
            "email": "carol@example.com",
            "password": "Password123!",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["message"].startswith("User logged in successfully")
    assert "access_token" in body
    assert body["user"]["email"] == "carol@example.com"


def test_login_user_wrong_password(monkeypatch):
    hashed = get_password_hash("Password123!")

    async def _find_one(filter=None, *args, **kwargs):
        return {
            "_id": "user_id",
            "email": "dave@example.com",
            "password": hashed,
            "role": "viewer",
        }

    monkeypatch.setattr("routes.users.users_collection.find_one", _find_one)

    resp = client.post(
        "/users/login",
        data={
            "email": "dave@example.com",
            "password": "WrongPass!",
        },
    )
    assert resp.status_code == 401


def test_login_user_not_found(monkeypatch):
    async def _find_one(filter=None, *args, **kwargs):
        return None

    monkeypatch.setattr("routes.users.users_collection.find_one", _find_one)

    resp = client.post(
        "/users/login",
        data={
            "email": "nobody@example.com",
            "password": "Password123!",
        },
    )
    assert resp.status_code == 404

from fastapi.testclient import TestClient
from main import app
from dependencies.authh import create_access_token, decode_token, verify_password, get_password_hash
import os
import time

client = TestClient(app)

def test_token_lifecycle():
    subject = "test_user_123"
    token = create_access_token(subject=subject)
    assert isinstance(token, str)
    assert len(token) > 0
    
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == subject

def test_password_hashing():
    password = "securepassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

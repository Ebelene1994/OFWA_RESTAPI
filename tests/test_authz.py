from fastapi.testclient import TestClient
from main import app
from dependencies.authz import require_analyst_role, require_viewer_or_analyst
from fastapi import HTTPException
import pytest

client = TestClient(app)

def test_require_analyst_role():
    # Helper to simulate dependency
    analyst_user = {"role": "analyst", "username": "analyst_dude"}
    viewer_user = {"role": "viewer", "username": "viewer_dude"}
    
    assert require_analyst_role(analyst_user) == analyst_user
    
    with pytest.raises(HTTPException) as excinfo:
        require_analyst_role(viewer_user)
    assert excinfo.value.status_code == 403

def test_require_viewer_or_analyst():
    analyst_user = {"role": "analyst"}
    viewer_user = {"role": "viewer"}
    other_user = {"role": "other"}
    
    assert require_viewer_or_analyst(analyst_user) == analyst_user
    assert require_viewer_or_analyst(viewer_user) == viewer_user
    
    with pytest.raises(HTTPException) as excinfo:
        require_viewer_or_analyst(other_user)
    assert excinfo.value.status_code == 403

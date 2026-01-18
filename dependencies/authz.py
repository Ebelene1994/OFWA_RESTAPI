from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated
from dependencies.authh import decode_token
from db import users_collection
from bson import ObjectId
from utils import replace_mongo_id

def is_authenticated(
    authorization: Annotated[
        HTTPAuthorizationCredentials, Depends(HTTPBearer(auto_error=False))
    ],
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated!"
        )
    payload = decode_token(authorization.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload["sub"]


async def authenticated_user(user_id: Annotated[str, Depends(is_authenticated)]):
    user = await users_collection.find_one(filter={"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user missing from database!",
        )
    return replace_mongo_id(user)


def require_analyst_role(user: Annotated[dict, Depends(authenticated_user)]):
    if user.get("role") != "analyst":
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Analyst role required",
        )
    return user

def require_viewer_or_analyst(user: Annotated[dict, Depends(authenticated_user)]):
    if user.get("role") not in ["analyst", "viewer"]:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Viewer or Analyst role required",
        )
    return user

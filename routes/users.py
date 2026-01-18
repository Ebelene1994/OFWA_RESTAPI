from enum import Enum
from fastapi import APIRouter, Form, status, HTTPException, Depends
from typing import Annotated
from pydantic import EmailStr
from db import users_collection
from utils import replace_mongo_id
from dependencies.authz import authenticated_user


class UserRole(str, Enum):
    ANALYST = "analyst"
    VIEWER = "viewer"


# Create users router
users_router = APIRouter(tags=["Users"])


# Define endpoints
from dependencies.authh import get_password_hash, verify_password, create_access_token

@users_router.post("/users/register")
async def register_user(
    username: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)],
    role: Annotated[UserRole, Form()] = UserRole.VIEWER,
):
    # Ensure user does not exist
    user_count = await users_collection.count_documents(filter={"email": email})
    if user_count > 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "User already exist!")
    # Hash user password
    hashed_password = get_password_hash(password)
    # Save user into database
    await users_collection.insert_one(
        {
            "username": username,
            "email": email,
            "password": hashed_password,
            "role": role.value,
        }
    )
    # Return response
    return {"message": "User registered successfully!"}


@users_router.post("/users/login")
async def login_user(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)],
):
    # Ensure user exist
    user = await users_collection.find_one(filter={"email": email})
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User does not exist!")
    # Compare their password
    correct_password = verify_password(password, user["password"])
    if not correct_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials!")
    # Generate for them an access token
    encoded_jwt = create_access_token(user["_id"])
    # Prepare user info to return
    user_info = replace_mongo_id(user)
    del user_info["password"]
    # Return reponse
    return {
        "message": "User logged in successfully!",
        "access_token": encoded_jwt,
        "user": user_info,
    }


@users_router.get("/users/profile")
def user_info(user: Annotated[dict, Depends(authenticated_user)]):
    # Prepare user info to return
    del user["password"]
    # Return reponse
    return user

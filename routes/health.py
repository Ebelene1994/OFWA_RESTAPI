from fastapi import APIRouter, status, Response
from db import db
from datetime import datetime, timezone
import os

health_router = APIRouter(
    prefix="/health",
    tags=["Health Check"]
)

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")


@health_router.get("", status_code=status.HTTP_200_OK)
async def get_health(response: Response):
    mongo_ok = await db.check_mongodb_health()
    if not mongo_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "api_status": "ok",
        "mongodb_status": "ok" if mongo_ok else "unavailable",
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

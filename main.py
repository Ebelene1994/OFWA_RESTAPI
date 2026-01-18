from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
from dotenv import load_dotenv
from config import settings
from routes.users import users_router
from routes import health, datasets, analysis
from db import db


# Configure cloudinary
load_dotenv()

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


app = FastAPI(
    title="OFWA Dashly",
    description=(
        "A FastAPI-based dashboard application for analyzing CSV datasets using "
        "generic statistical methods."
    ),
    openapi_tags=[
        {"name": "Health Check"},
        {"name": "Home"},
        {"name": "Users"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    print("OFWA Dashly API is running")

@app.on_event("shutdown")
async def on_shutdown():
    try:
        db.close()
    except Exception:
        pass


@app.get("/", tags=["Home"])
def get_home():
    return {"message": "You are on the home page"}


# Include routers
app.include_router(users_router)
app.include_router(health.health_router)
app.include_router(datasets.datasets_router)
app.include_router(analysis.analysis_router)


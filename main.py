from fastapi import FastAPI
import cloudinary
from config import settings
from routes.users import users_router
from routes import health, datasets, analysis


# Configure cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


app = FastAPI()


@app.get("/")
def get_home():
    return {"message": "You are on the home page"}


# Include routers
app.include_router(users_router)
app.include_router(health.health_router)
app.include_router(datasets.datasets_router)
app.include_router(analysis.analysis_router)


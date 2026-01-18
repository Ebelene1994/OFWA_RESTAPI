from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from typing import List
from services.cloudinary_service import CloudinaryService
from services.csv_analysis_service import CSVAnalysisService
from models.dataset_model import Dataset
# from dependencies.authz import authenticated_user # Uncomment when ready

datasets_router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"]
)

@datasets_router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        # Upload to Cloudinary
        upload_result = CloudinaryService.upload_file(file)
        
        # Analyze content (optional step here, or separate)
        # file.file.seek(0)
        # content = file.file.read().decode('utf-8')
        # analysis = CSVAnalysisService.analyze_content(content)
        
        return {
            "message": "File uploaded successfully",
            "url": upload_result.get("url"),
            "public_id": upload_result.get("public_id"),
            # "analysis_summary": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

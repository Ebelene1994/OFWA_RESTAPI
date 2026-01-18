from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Form
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
from services.cloudinary_service import CloudinaryService
from services.csv_analysis_service import CSVAnalysisService
from models.dataset_model import Dataset
from dependencies.authz import require_analyst_role
from db import ofwa_dash_db

datasets_collection = ofwa_dash_db["datasets"]

datasets_router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"]
)

@datasets_router.post("/upload", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_analyst_role)])
async def upload_dataset(
    file: UploadFile = File(...),
    analysis_type: str = Form("summary"),
    params: Optional[str] = Form(None),
    user: Dict[str, Any] = Depends(require_analyst_role),
):
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed for analysis upload")
    
    try:
        # Parse analysis parameters (JSON string in multipart form)
        parsed_params: Dict[str, Any] = {}
        if params:
            try:
                parsed_params = json.loads(params)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in 'params' field")

        # Read content for analysis
        content_bytes = await file.read()
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = content_bytes.decode("utf-8", errors="ignore")
        # Reset pointer so Cloudinary can read the file
        try:
            file.file.seek(0)
        except Exception:
            pass

        # Upload to Cloudinary (sync method kept for test compatibility)
        upload_result = CloudinaryService.upload_file(file)

        # Trigger analysis
        if analysis_type == "galamsay":
            analysis = CSVAnalysisService.analyze_galamsay(
                content,
                city_column=parsed_params.get("city_column", "city"),
                region_column=parsed_params.get("region_column", "region"),
                sites_column=parsed_params.get("sites_column", "sites"),
                threshold=int(parsed_params.get("threshold", 10)),
            )
        else:
            analysis = CSVAnalysisService.analyze_content(content)

        # Store metadata and results
        doc = {
            "filename": file.filename,
            "cloudinary_url": upload_result.get("url"),
            "public_id": upload_result.get("public_id"),
            "uploaded_by": user.get("id"),
            "upload_timestamp": datetime.now(timezone.utc),
            "content_type": file.content_type,
            "analysis": {
                "type": analysis_type,
                "parameters": parsed_params,
                "results": analysis,
            },
        }
        insert_res = await datasets_collection.insert_one(doc)

        return {
            "message": "File uploaded and analyzed successfully",
            "url": upload_result.get("url"),
            "public_id": upload_result.get("public_id"),
            "dataset_id": str(insert_res.inserted_id),
            "analysis": analysis,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

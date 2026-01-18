from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict, Any, Optional
from models.analysis_model import AnalysisRequest, AnalysisResult
from services.csv_analysis_service import CSVAnalysisService
from dependencies.authz import require_analyst_role, require_viewer_or_analyst
from db import ofwa_dash_db
from datetime import datetime
from bson import ObjectId

analysis_router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)

@analysis_router.post("/perform", response_model=AnalysisResult, dependencies=[Depends(require_analyst_role)])
async def perform_analysis(request: AnalysisRequest):
    # Retrieve dataset content (mock logic here, in real app fetch from DB/Cloudinary)
    # content = get_dataset_content(request.dataset_id) 
    
    # Mock content for demonstration
    mock_csv_content = "col1,col2\n1,2\n3,4"
    
    if request.analysis_type == "summary":
        result = CSVAnalysisService.analyze_content(mock_csv_content)
    elif request.analysis_type == "correlation":
        result = CSVAnalysisService.get_correlations(mock_csv_content)
    else:
        raise HTTPException(status_code=400, detail="Invalid analysis type")
        
    return {
        "id": "analysis_123",
        "dataset_id": request.dataset_id,
        "analysis_type": request.analysis_type,
        "result_data": result,
        "created_at": "2023-01-01T00:00:00",
        "performed_by": "user_1"
    }


# Collections
analysis_logs_collection = ofwa_dash_db["analysis_logs"]
datasets_collection = ofwa_dash_db["datasets"]


def _serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if isinstance(dt, datetime) else None


def _attach_cloudinary_urls(logs: List[Dict[str, Any]], datasets_by_id: Dict[str, Dict[str, Any]]):
    for log in logs:
        ds = datasets_by_id.get(log.get("dataset_id"))
        if ds:
            log["cloudinary_url"] = ds.get("cloudinary_url")


@analysis_router.get("/latest", dependencies=[Depends(require_viewer_or_analyst)])
async def get_latest_analysis():
    doc = await analysis_logs_collection.find_one(sort=[("executed_at", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No analysis logs found")

    # Fetch dataset for URL
    dataset = None
    if doc.get("dataset_id"):
        ds_id = doc.get("dataset_id")
        try:
            dataset = await datasets_collection.find_one({"_id": ObjectId(ds_id)})
        except Exception:
            dataset = await datasets_collection.find_one({"_id": ds_id})

    # Build response
    resp = {
        "analysis_id": doc.get("analysis_id"),
        "dataset_id": doc.get("dataset_id"),
        "analyst_user_id": doc.get("analyst_user_id"),
        "parameters": doc.get("parameters"),
        "results": doc.get("results"),
        "executed_at": _serialize_datetime(doc.get("executed_at")),
        "status": doc.get("status"),
        "cloudinary_url": dataset.get("cloudinary_url") if dataset else None,
    }
    return resp


@analysis_router.get("/history", dependencies=[Depends(require_viewer_or_analyst)])
async def get_analysis_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    skip = (page - 1) * page_size

    cursor = (
        analysis_logs_collection
        .find({})
        .sort("executed_at", -1)
        .skip(skip)
        .limit(page_size)
    )
    docs = await cursor.to_list(length=page_size)

    # Collect dataset_ids and fetch URLs in batch
    dataset_ids = [d.get("dataset_id") for d in docs if d.get("dataset_id")]
    datasets_by_id: Dict[str, Dict[str, Any]] = {}
    if dataset_ids:
        ds_cursor = datasets_collection.find({})
        datasets = await ds_cursor.to_list(length=1000)
        for ds in datasets:
            key = str(ds.get("_id"))
            datasets_by_id[key] = ds

    items: List[Dict[str, Any]] = []
    for d in docs:
        item = {
            "analysis_id": d.get("analysis_id"),
            "dataset_id": d.get("dataset_id"),
            "analyst_user_id": d.get("analyst_user_id"),
            "parameters": d.get("parameters"),
            "results": d.get("results"),
            "executed_at": _serialize_datetime(d.get("executed_at")),
            "status": d.get("status"),
            "cloudinary_url": None,
        }
        ds = datasets_by_id.get(d.get("dataset_id"))
        if ds:
            item["cloudinary_url"] = ds.get("cloudinary_url")
        items.append(item)

    total_count = await analysis_logs_collection.count_documents({})
    return {
        "page": page,
        "page_size": page_size,
        "total": total_count,
        "items": items,
    }


@analysis_router.get("/{analysis_id}", dependencies=[Depends(require_viewer_or_analyst)])
async def get_analysis_by_id(analysis_id: str):
    doc = await analysis_logs_collection.find_one({"analysis_id": analysis_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Analysis not found")

    dataset = None
    if doc.get("dataset_id"):
        ds_id = doc.get("dataset_id")
        try:
            dataset = await datasets_collection.find_one({"_id": ObjectId(ds_id)})
        except Exception:
            dataset = await datasets_collection.find_one({"_id": ds_id})

    return {
        "analysis_id": doc.get("analysis_id"),
        "dataset_id": doc.get("dataset_id"),
        "analyst_user_id": doc.get("analyst_user_id"),
        "parameters": doc.get("parameters"),
        "results": doc.get("results"),
        "executed_at": _serialize_datetime(doc.get("executed_at")),
        "status": doc.get("status"),
        "cloudinary_url": dataset.get("cloudinary_url") if dataset else None,
    }

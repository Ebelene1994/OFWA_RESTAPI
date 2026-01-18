from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class AnalysisRequest(BaseModel):
    dataset_id: str
    analysis_type: str  # e.g., "summary", "correlation", "regression"
    columns: Optional[List[str]] = None
    params: Optional[Dict[str, Any]] = None

class AnalysisResult(BaseModel):
    id: str
    dataset_id: str
    analysis_type: str
    result_data: Dict[str, Any]
    created_at: datetime
    performed_by: str # User ID

    class Config:
        from_attributes = True

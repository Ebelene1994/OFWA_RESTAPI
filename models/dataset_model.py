from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DatasetBase(BaseModel):
    filename: str
    description: Optional[str] = None

class DatasetCreate(DatasetBase):
    pass

class DatasetUpdate(BaseModel):
    description: Optional[str] = None

class DatasetInDB(DatasetBase):
    id: str
    file_url: str
    uploaded_by: str  # User ID
    upload_date: datetime
    file_size: int
    content_type: str
    
    class Config:
        from_attributes = True

class Dataset(DatasetInDB):
    pass


class DatasetMetadata(BaseModel):
    dataset_id: str
    original_filename: str
    cloudinary_url: str
    uploaded_by: str
    upload_timestamp: datetime
    analysis_parameters: Optional[Dict[str, Any]] = None

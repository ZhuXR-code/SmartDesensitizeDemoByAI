from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DataSourceCreate(BaseModel):
    name: str
    source_type: str
    config: Dict[str, Any]


class DataSourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    config: Dict[str, Any]
    is_active: bool
    created_at: datetime


class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: str
    source_id: Optional[int] = None
    encoding: Optional[str] = "utf-8"


class DatasetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    source_type: str
    file_path: Optional[str]
    file_size: Optional[int]
    row_count: Optional[int]
    column_count: Optional[int]
    columns: Optional[List[str]]
    encoding: str
    preview_data: Optional[List[Dict]]
    is_active: bool
    created_at: datetime

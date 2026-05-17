from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ResponseModel(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PaginationResponse(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int
    items: List[Any]

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DetectionRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    language: str
    rule_type: str
    pattern: Optional[str] = None
    keywords: Optional[List[str]] = None
    example: Optional[str] = None


class DetectionRuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    language: str
    rule_type: str
    pattern: Optional[str]
    keywords: Optional[List[str]]
    example: Optional[str]
    is_builtin: bool
    is_active: bool
    created_at: datetime


class DetectionRuleSetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rules: List[int]
    scenario: Optional[str] = None


class DetectionRuleSetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    rules: List[int]
    scenario: Optional[str]
    is_active: bool
    created_at: datetime


class DetectionTaskCreate(BaseModel):
    name: str
    dataset_id: int
    rule_set_id: Optional[int] = None
    scan_columns: Optional[list] = None  # 改为 list 而不是 List[str]，更宽松
    language_strategy: str = "auto"
    
    class Config:
        arbitrary_types_allowed = True


class DetectionTaskResponse(BaseModel):
    id: int
    name: str
    dataset_id: int
    rule_set_id: Optional[int]
    scan_columns: Optional[List[str]]
    language_strategy: str
    status: str
    progress: float
    scanned_rows: int
    total_rows: int
    found_count: int
    language_distribution: Optional[Dict]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]  # 耗时（秒），精确到小数点后3位
    created_at: datetime


class DetectionResultResponse(BaseModel):
    id: int
    task_id: int
    dataset_id: int
    row_index: int
    column_name: str
    detected_language: str
    rule_id: int
    rule_name: str
    rule_type: str
    matched_content: str
    confidence: float
    desensitization_suggestion: str
    created_at: datetime

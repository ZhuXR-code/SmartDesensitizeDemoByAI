from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DesensitizationRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    language: str
    category: str
    method: str
    config: Optional[Dict[str, Any]] = None


class DesensitizationRuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    language: str
    category: str
    method: str
    config: Optional[Dict[str, Any]]
    is_builtin: bool
    is_active: bool
    created_at: datetime


class DesensitizationTaskCreate(BaseModel):
    name: str
    dataset_id: int
    source_type: str = "dataset"
    detection_task_id: Optional[int] = None
    field_rules: Optional[Dict[str, int]] = {}  # 手动模式使用
    auto_detect: Optional[bool] = False  # 自动识别模式
    output_mode: str = "copy"
    key_id: Optional[int] = None


class DesensitizationTaskResponse(BaseModel):
    id: int
    name: str
    dataset_id: int
    source_type: str
    detection_task_id: Optional[int]
    field_rules: Dict[str, int]
    output_mode: str
    key_id: Optional[int]
    status: str
    progress: float
    processed_rows: int
    total_rows: int
    output_path: Optional[str]
    temp_file_path: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]  # 耗时（秒），精确到小数点后3位
    created_at: datetime


class PreviewRequest(BaseModel):
    dataset_id: int
    field_rules: Optional[Dict[str, int]] = {}  # 手动模式使用
    auto_detect: Optional[bool] = False  # 自动识别模式
    key_id: Optional[int] = None
    limit: int = 10


class PreviewResponse(BaseModel):
    row_index: int
    columns: Dict[str, Dict[str, str]]

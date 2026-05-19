from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class AiConfigCreate(BaseModel):
    alias: str = ""
    provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    api_key: str
    api_base_url: Optional[str] = ""
    enable_web_search: bool = False
    temperature: float = 0.3
    max_tokens: int = 4096


class AiConfigUpdate(BaseModel):
    alias: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    enable_web_search: Optional[bool] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class AiConfigTest(BaseModel):
    provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    api_key: str
    api_base_url: Optional[str] = ""
    temperature: float = 0.3
    max_tokens: int = 4096
    test_text: Optional[str] = "Hello, this is a test message."


class AiDetectionTaskCreate(BaseModel):
    name: str
    dataset_id: int
    ai_config_id: Optional[int] = None
    enable_web_search: bool = False
    custom_prompt: Optional[str] = None


class AiDesensitizationCreate(BaseModel):
    name: str
    detection_task_id: int
    mode: str = "mask"
    ai_config_id: int = None  # 可选，不传则使用默认配置
    output_format: str = "xlsx"

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float
from app.db.database import Base
from datetime import datetime


class DesensitizationRule(Base):
    __tablename__ = "desensitization_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    language = Column(String(10), nullable=False)
    category = Column(String(20), nullable=False)
    desensitization_method = Column(String(50))  # 脱敏方式: full_mask, simulation, partial_mask
    method = Column(String(50), nullable=False)
    config = Column(JSON)
    example = Column(JSON)  # 脱敏示例: {"before": "原始数据", "after": "脱敏后数据"}
    usage_count = Column(Integer, default=0)  # 使用次数统计
    is_builtin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class DesensitizationKey(Base):
    __tablename__ = "desensitization_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String(50), nullable=False)
    key_hash = Column(String(255), nullable=False)
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class DesensitizationTask(Base):
    __tablename__ = "desensitization_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    dataset_id = Column(Integer, nullable=False)
    source_type = Column(String(20), default="dataset")
    detection_task_id = Column(Integer)
    field_rules = Column(JSON)
    output_mode = Column(String(20), default="copy")
    key_id = Column(Integer)
    status = Column(String(20), default="pending")
    progress = Column(Float, default=0.0)
    processed_rows = Column(Integer, default=0)
    total_rows = Column(Integer, default=0)
    output_path = Column(String(500))
    temp_file_path = Column(String(500))
    report_path = Column(String(500))  # 报告文件路径
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)  # 耗时（秒），精确到小数点后3位
    logs = Column(Text)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)


class DesensitizationResult(Base):
    __tablename__ = "desensitization_results"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, nullable=False)
    dataset_id = Column(Integer, nullable=False)
    column_name = Column(String(100))
    original_value = Column(String(500))
    desensitized_value = Column(String(500))
    rule_id = Column(Integer)
    rule_name = Column(String(100))
    row_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

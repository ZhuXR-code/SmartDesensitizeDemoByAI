from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float
from app.db.database import Base
from datetime import datetime


class DetectionRule(Base):
    __tablename__ = "detection_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    language = Column(String(10), nullable=False)
    rule_type = Column(String(20), nullable=False)
    pattern = Column(Text, nullable=False)
    keywords = Column(JSON)
    example = Column(String(255))
    is_builtin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class DetectionRuleSet(Base):
    __tablename__ = "detection_rule_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    rules = Column(JSON)
    scenario = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class DetectionTask(Base):
    __tablename__ = "detection_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    dataset_id = Column(Integer, nullable=False)
    rule_set_id = Column(Integer)
    scan_columns = Column(JSON)
    language_strategy = Column(String(20), default="auto")
    status = Column(String(20), default="pending")
    progress = Column(Float, default=0.0)
    scanned_rows = Column(Integer, default=0)
    total_rows = Column(Integer, default=0)
    found_count = Column(Integer, default=0)
    language_distribution = Column(JSON)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)  # 耗时（秒），精确到小数点后3位
    logs = Column(Text)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)


class DetectionResult(Base):
    __tablename__ = "detection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, nullable=False)
    dataset_id = Column(Integer, nullable=False)
    row_index = Column(Integer)
    column_name = Column(String(100))
    detected_language = Column(String(10))
    rule_id = Column(Integer)
    rule_name = Column(String(100))
    rule_type = Column(String(20))
    matched_content = Column(String(500))
    confidence = Column(Float)
    desensitization_suggestion = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

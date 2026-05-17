from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float
from app.db.database import Base
from datetime import datetime


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    report_type = Column(String(20), nullable=False)
    task_id = Column(Integer, nullable=False)
    dataset_id = Column(Integer)
    summary = Column(JSON)
    details = Column(JSON)
    file_path = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from app.db.database import Base
from datetime import datetime


class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    source_type = Column(String(20), nullable=False)
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    source_id = Column(Integer)
    source_type = Column(String(20), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)
    row_count = Column(Integer)
    column_count = Column(Integer)
    columns = Column(JSON)
    encoding = Column(String(20), default="utf-8")
    preview_data = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

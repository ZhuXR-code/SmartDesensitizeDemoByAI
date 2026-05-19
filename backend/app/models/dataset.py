from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from app.db.database import Base
from datetime import datetime


class DataSource(Base):
    __tablename__ = "data_sources"
    __table_args__ = {"comment": "数据源配置表"}

    id = Column(Integer, primary_key=True, index=True, comment="数据源ID")
    name = Column(String(100), nullable=False, comment="数据源名称")
    source_type = Column(String(20), nullable=False, comment="数据源类型：database/file")
    config = Column(JSON, comment="连接配置信息")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class Dataset(Base):
    __tablename__ = "datasets"
    __table_args__ = {"comment": "数据集表"}

    id = Column(Integer, primary_key=True, index=True, comment="数据集ID")
    name = Column(String(100), nullable=False, comment="数据集名称")
    description = Column(String(500), comment="数据集描述")
    source_id = Column(Integer, comment="关联数据源ID")
    source_type = Column(String(20), nullable=False, comment="来源类型：upload/database")
    file_path = Column(String(500), comment="文件存储路径")
    file_size = Column(Integer, comment="文件大小（字节）")
    row_count = Column(Integer, comment="数据行数")
    column_count = Column(Integer, comment="列数")
    columns = Column(JSON, comment="列名列表")
    encoding = Column(String(20), default="utf-8", comment="文件编码")
    preview_data = Column(JSON, comment="预览数据")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

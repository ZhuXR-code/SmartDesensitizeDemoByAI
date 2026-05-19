from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float
from app.db.database import Base
from datetime import datetime


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = {"comment": "报表记录表"}

    id = Column(Integer, primary_key=True, index=True, comment="报表ID")
    name = Column(String(100), nullable=False, comment="报表名称")
    report_type = Column(String(20), nullable=False, comment="报表类型：detection/desensitization/compliance")
    task_id = Column(Integer, nullable=False, comment="关联任务ID")
    dataset_id = Column(Integer, comment="关联数据集ID")
    summary = Column(JSON, comment="报表摘要数据")
    details = Column(JSON, comment="报表详细数据")
    file_path = Column(String(500), comment="报表文件路径")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_by = Column(Integer, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float
from app.db.database import Base
from datetime import datetime


class DesensitizationRule(Base):
    __tablename__ = "desensitization_rules"
    __table_args__ = {"comment": "数据脱敏规则表"}

    id = Column(Integer, primary_key=True, index=True, comment="规则ID")
    name = Column(String(100), nullable=False, comment="规则名称")
    description = Column(String(500), comment="规则描述")
    language = Column(String(10), nullable=False, comment="语言类型")
    category = Column(String(20), nullable=False, comment="规则分类：name/phone/idcard/address等")
    desensitization_method = Column(String(50), comment="脱敏方式：full_mask/simulation/partial_mask")
    method = Column(String(50), nullable=False, comment="具体脱敏方法")
    config = Column(JSON, comment="脱敏配置参数")
    example = Column(JSON, comment="脱敏示例：{before, after}")
    usage_count = Column(Integer, default=0, comment="使用次数统计")
    is_builtin = Column(Boolean, default=False, comment="是否内置规则")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_by = Column(Integer, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class DesensitizationKey(Base):
    __tablename__ = "desensitization_keys"
    __table_args__ = {"comment": "脱敏密钥表"}

    id = Column(Integer, primary_key=True, index=True, comment="密钥ID")
    alias = Column(String(50), nullable=False, comment="密钥别名")
    key_hash = Column(String(255), nullable=False, comment="密钥哈希值")
    description = Column(String(255), comment="密钥描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class DesensitizationTask(Base):
    __tablename__ = "desensitization_tasks"
    __table_args__ = {"comment": "数据脱敏任务表"}

    id = Column(Integer, primary_key=True, index=True, comment="任务ID")
    name = Column(String(100), nullable=False, comment="任务名称")
    dataset_id = Column(Integer, nullable=False, comment="关联数据集ID")
    source_type = Column(String(20), default="dataset", comment="数据来源类型")
    detection_task_id = Column(Integer, comment="关联的识别任务ID")
    field_rules = Column(JSON, comment="字段与脱敏规则映射")
    output_mode = Column(String(20), default="copy", comment="输出模式：copy/overwrite")
    key_id = Column(Integer, comment="使用的密钥ID")
    status = Column(String(20), default="pending", comment="任务状态")
    progress = Column(Float, default=0.0, comment="处理进度百分比")
    processed_rows = Column(Integer, default=0, comment="已处理行数")
    total_rows = Column(Integer, default=0, comment="总行数")
    output_path = Column(String(500), comment="输出文件路径")
    temp_file_path = Column(String(500), comment="临时文件路径")
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")
    duration_seconds = Column(Float, comment="耗时（秒）")
    logs = Column(Text, comment="执行日志")
    created_by = Column(Integer, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class DesensitizationResult(Base):
    __tablename__ = "desensitization_results"
    __table_args__ = {"comment": "数据脱敏结果明细表"}

    id = Column(Integer, primary_key=True, index=True, comment="结果ID")
    task_id = Column(Integer, nullable=False, comment="关联任务ID")
    dataset_id = Column(Integer, nullable=False, comment="关联数据集ID")
    column_name = Column(String(100), comment="列名")
    original_value = Column(String(500), comment="原始值")
    desensitized_value = Column(String(500), comment="脱敏后的值")
    rule_id = Column(Integer, comment="使用的规则ID")
    rule_name = Column(String(100), comment="使用的规则名称")
    row_index = Column(Integer, comment="数据行号")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

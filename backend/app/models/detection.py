from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float
from app.db.database import Base
from datetime import datetime


class DetectionRule(Base):
    __tablename__ = "detection_rules"
    __table_args__ = {"comment": "敏感数据识别规则表"}

    id = Column(Integer, primary_key=True, index=True, comment="规则ID")
    name = Column(String(100), nullable=False, comment="规则名称")
    description = Column(String(500), comment="规则描述")
    language = Column(String(10), nullable=False, comment="语言类型：zh/en/jp等")
    rule_type = Column(String(20), nullable=False, comment="规则类型：regex/keyword/pattern")
    pattern = Column(Text, nullable=False, comment="正则表达式或模式")
    keywords = Column(JSON, comment="关键词列表")
    example = Column(String(255), comment="匹配示例")
    is_builtin = Column(Boolean, default=False, comment="是否内置规则")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_by = Column(Integer, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class DetectionRuleSet(Base):
    __tablename__ = "detection_rule_sets"
    __table_args__ = {"comment": "识别规则集表"}

    id = Column(Integer, primary_key=True, index=True, comment="规则集ID")
    name = Column(String(100), nullable=False, comment="规则集名称")
    description = Column(String(500), comment="规则集描述")
    rules = Column(JSON, comment="包含的规则ID列表")
    scenario = Column(String(50), comment="应用场景：finance/healthcare/general等")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_by = Column(Integer, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class DetectionTask(Base):
    __tablename__ = "detection_tasks"
    __table_args__ = {"comment": "敏感数据识别任务表"}

    id = Column(Integer, primary_key=True, index=True, comment="任务ID")
    name = Column(String(100), nullable=False, comment="任务名称")
    dataset_id = Column(Integer, nullable=False, comment="关联数据集ID")
    rule_set_id = Column(Integer, comment="使用的规则集ID")
    scan_columns = Column(JSON, comment="扫描的列名列表")
    language_strategy = Column(String(20), default="auto", comment="语言策略：auto/manual")
    status = Column(String(20), default="pending", comment="任务状态：pending/running/completed/failed")
    progress = Column(Float, default=0.0, comment="处理进度百分比")
    scanned_rows = Column(Integer, default=0, comment="已扫描行数")
    total_rows = Column(Integer, default=0, comment="总行数")
    found_count = Column(Integer, default=0, comment="发现敏感数据条数")
    language_distribution = Column(JSON, comment="语言分布统计")
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")
    duration_seconds = Column(Float, comment="总耗时（秒）")
    logs = Column(Text, comment="执行日志")
    created_by = Column(Integer, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class DetectionResult(Base):
    __tablename__ = "detection_results"
    __table_args__ = {"comment": "敏感数据识别结果表"}

    id = Column(Integer, primary_key=True, index=True, comment="结果ID")
    task_id = Column(Integer, nullable=False, comment="关联任务ID")
    dataset_id = Column(Integer, nullable=False, comment="关联数据集ID")
    row_index = Column(Integer, comment="数据行号")
    column_name = Column(String(100), comment="列名")
    detected_language = Column(String(10), comment="检测到的语言")
    rule_id = Column(Integer, comment="匹配的规则ID")
    rule_name = Column(String(100), comment="匹配的规则名称")
    rule_type = Column(String(20), comment="匹配的规则类型")
    matched_content = Column(String(500), comment="匹配到的内容片段")
    confidence = Column(Float, comment="置信度（0-1）")
    desensitization_suggestion = Column(String(100), comment="建议的脱敏方式")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

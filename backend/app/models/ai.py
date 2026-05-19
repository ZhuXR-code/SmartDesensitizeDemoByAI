from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float, ForeignKey
from app.db.database import Base
from datetime import datetime


class AiConfig(Base):
    __tablename__ = "ai_configs"
    __table_args__ = {"comment": "AI模型配置表"}

    id = Column(Integer, primary_key=True, index=True, comment="配置ID")
    alias = Column(String(100), default="", comment="配置别名/名称")
    provider = Column(String(50), nullable=False, default="openai", comment="AI提供商：openai/deepseek/qwen/kimi等")
    model_name = Column(String(100), nullable=False, default="gpt-4o-mini", comment="模型名称")
    api_key = Column(String(500), nullable=False, comment="API密钥")
    api_base_url = Column(String(500), default="", comment="API基础地址")
    enable_web_search = Column(Boolean, default=False, comment="是否启用联网搜索")
    enable_thinking = Column(Boolean, default=False, comment="是否启用DeepSeek思考模式")
    temperature = Column(Float, default=0.3, comment="模型温度参数(0-1)")
    max_tokens = Column(Integer, default=4096, comment="最大输出Token数")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class AiDetectionTask(Base):
    __tablename__ = "ai_detection_tasks"
    __table_args__ = {"comment": "AI智能识别任务表"}

    id = Column(Integer, primary_key=True, index=True, comment="任务ID")
    name = Column(String(100), nullable=False, comment="任务名称")
    dataset_id = Column(Integer, nullable=False, comment="关联数据集ID")
    dataset_name = Column(String(100), default="", comment="数据集名称")
    status = Column(String(20), default="pending", comment="任务状态")
    progress = Column(Float, default=0.0, comment="处理进度百分比")
    total_rows = Column(Integer, default=0, comment="总行数")
    processed_rows = Column(Integer, default=0, comment="已处理行数")
    found_count = Column(Integer, default=0, comment="发现敏感数据条数")
    enable_web_search = Column(Boolean, default=False, comment="是否启用联网搜索")
    enable_thinking = Column(Boolean, default=False, comment="是否启用DeepSeek思考模式")
    prompt_template = Column(Text, default="", comment="自定义提示词模板")
    model_used = Column(String(100), default="", comment="使用的模型名称")
    result_summary = Column(JSON, comment="检测结果摘要统计")
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")
    duration_seconds = Column(Float, comment="总耗时（秒）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class AiDetectionResult(Base):
    __tablename__ = "ai_detection_results"
    __table_args__ = {"comment": "AI智能识别结果表"}

    id = Column(Integer, primary_key=True, index=True, comment="结果ID")
    task_id = Column(Integer, nullable=False, comment="关联任务ID")
    row_index = Column(Integer, comment="数据行号")
    column_name = Column(String(100), comment="列名")
    original_value = Column(String(1000), comment="原始值")
    is_sensitive = Column(Boolean, default=False, comment="是否敏感数据")
    sensitive_type = Column(String(100), default="", comment="敏感数据类型")
    confidence = Column(Float, default=0.0, comment="置信度(0-1)")
    risk_level = Column(String(20), default="low", comment="风险等级：high/moderate/low")
    regulation_ref = Column(String(500), default="", comment="法规依据引用")
    llm_reasoning = Column(Text, default="", comment="AI推理过程")
    desensitization_suggestion = Column(String(50), default="", comment="脱敏建议：mask/synthetic")
    reviewed = Column(Boolean, default=False, comment="是否已人工复核")
    review_result = Column(Boolean, default=None, comment="复核结果：True=敏感，False=非敏感，None=未复核")
    review_reason = Column(String(500), default="", comment="人工复核理由")
    reviewed_at = Column(DateTime, comment="复核时间")
    reviewed_by = Column(Integer, comment="复核人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class AiDesensitizationTask(Base):
    __tablename__ = "ai_desensitization_tasks"
    __table_args__ = {"comment": "AI智能脱敏任务表"}

    id = Column(Integer, primary_key=True, index=True, comment="任务ID")
    name = Column(String(100), nullable=False, comment="任务名称")
    detection_task_id = Column(Integer, nullable=False, comment="关联的AI检测任务ID")
    mode = Column(String(20), nullable=False, comment="脱敏模式：mask/synthetic/correlated_synthetic")
    ai_config_id = Column(Integer, nullable=True, comment="使用的AI配置ID，为空则使用默认配置")
    status = Column(String(20), default="pending", comment="任务状态")
    progress = Column(Float, default=0.0, comment="处理进度百分比")
    total_rows = Column(Integer, default=0, comment="总行数")
    processed_rows = Column(Integer, default=0, comment="已处理行数")
    output_file_path = Column(String(500), default="", comment="输出文件路径（对比文件）")
    output_file_pure_path = Column(String(500), nullable=True, comment="纯脱敏文件路径")
    output_file_format = Column(String(20), default="xlsx", comment="输出文件格式")
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")
    duration_seconds = Column(Float, comment="总耗时（秒）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class AiDesensitizationResult(Base):
    __tablename__ = "ai_desensitization_results"
    __table_args__ = {"comment": "AI智能脱敏结果表"}

    id = Column(Integer, primary_key=True, index=True, comment="结果ID")
    task_id = Column(Integer, nullable=False, comment="关联任务ID")
    row_index = Column(Integer, comment="数据行号")
    column_name = Column(String(100), comment="列名")
    original_value = Column(String(1000), comment="原始值")
    desensitized_value = Column(String(1000), comment="脱敏后的值")
    method = Column(String(20), default="", comment="脱敏方法")
    ai_original_is_sensitive = Column(Boolean, default=False, comment="AI原始识别是否敏感")
    ai_original_sensitive_type = Column(String(100), default="", comment="AI原始识别敏感类型")
    review_result = Column(Boolean, default=None, comment="人工复核结果：True=敏感，False=非敏感")
    review_status = Column(String(20), default="unreviewed", comment="复核状态：unreviewed/reviewed")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

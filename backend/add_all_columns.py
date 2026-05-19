from sqlalchemy import create_engine, text
from app.core.config import settings

# 创建数据库连接
db_url = settings.DATABASE_URL
engine = create_engine(db_url, pool_pre_ping=True)

# 需要添加的字段列表
alter_statements = [
    # ai_detection_results 表
    """
    ALTER TABLE ai_detection_results 
    ADD COLUMN reviewed BOOLEAN DEFAULT FALSE COMMENT '是否已人工复核'
    """,
    """
    ALTER TABLE ai_detection_results 
    ADD COLUMN review_result BOOLEAN DEFAULT NULL COMMENT '复核结果：True=敏感，False=非敏感，None=未复核'
    """,
    """
    ALTER TABLE ai_detection_results 
    ADD COLUMN review_reason VARCHAR(500) DEFAULT '' COMMENT '人工复核理由'
    """,
    """
    ALTER TABLE ai_detection_results 
    ADD COLUMN reviewed_at DATETIME COMMENT '复核时间'
    """,
    """
    ALTER TABLE ai_detection_results 
    ADD COLUMN reviewed_by INT COMMENT '复核人ID'
    """,
    # ai_desensitization_results 表
    """
    ALTER TABLE ai_desensitization_results 
    ADD COLUMN ai_original_is_sensitive BOOLEAN DEFAULT FALSE COMMENT 'AI原始识别是否敏感'
    """,
    """
    ALTER TABLE ai_desensitization_results 
    ADD COLUMN ai_original_sensitive_type VARCHAR(100) DEFAULT '' COMMENT 'AI原始识别敏感类型'
    """,
    """
    ALTER TABLE ai_desensitization_results 
    ADD COLUMN review_result BOOLEAN DEFAULT NULL COMMENT '人工复核结果：True=敏感，False=非敏感'
    """,
    """
    ALTER TABLE ai_desensitization_results 
    ADD COLUMN review_status VARCHAR(20) DEFAULT 'unreviewed' COMMENT '复核状态：unreviewed/reviewed'
    """,
]

with engine.connect() as conn:
    for sql in alter_statements:
        try:
            conn.execute(text(sql))
            conn.commit()
            print(f"Success: {sql.strip()[:60]}...")
        except Exception as e:
            print(f"Skipped: {sql.strip()[:60]}... - {str(e)[:100]}")

print("Done!")

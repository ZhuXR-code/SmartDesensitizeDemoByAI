from sqlalchemy import create_engine, text
from app.core.config import settings

# 创建数据库连接
db_url = settings.DATABASE_URL
engine = create_engine(db_url, pool_pre_ping=True)

# 添加字段
with engine.connect() as conn:
    try:
        conn.execute(text("""
            ALTER TABLE ai_desensitization_tasks 
            ADD COLUMN output_file_pure_path VARCHAR(500) DEFAULT '' COMMENT '纯脱敏文件路径'
        """))
        conn.commit()
        print("Field added successfully")
    except Exception as e:
        print(f"Field may already exist or other error: {e}")

"""
添加 enable_thinking 字段到 ai_configs 和 ai_detection_tasks 表
用于支持 DeepSeek 思考模式开关
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def upgrade():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='ai_configs' AND column_name='enable_thinking'
        """))
        
        if not result.fetchone():
            # 添加到 ai_configs 表
            conn.execute(text("""
                ALTER TABLE ai_configs 
                ADD COLUMN enable_thinking BOOLEAN DEFAULT FALSE 
                COMMENT '是否启用DeepSeek思考模式'
            """))
            print("✓ 已添加 enable_thinking 字段到 ai_configs 表")
        else:
            print("○ ai_configs 表中 enable_thinking 字段已存在")
        
        # 检查 ai_detection_tasks 表
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='ai_detection_tasks' AND column_name='enable_thinking'
        """))
        
        if not result.fetchone():
            # 添加到 ai_detection_tasks 表
            conn.execute(text("""
                ALTER TABLE ai_detection_tasks 
                ADD COLUMN enable_thinking BOOLEAN DEFAULT FALSE 
                COMMENT '是否启用DeepSeek思考模式'
            """))
            print("✓ 已添加 enable_thinking 字段到 ai_detection_tasks 表")
        else:
            print("○ ai_detection_tasks 表中 enable_thinking 字段已存在")
        
        conn.commit()
    
    print("\n迁移完成！")

if __name__ == "__main__":
    upgrade()

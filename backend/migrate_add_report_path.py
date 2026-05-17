"""
添加脱敏任务报告路径字段
"""
from sqlalchemy import text
from app.db.database import engine

def upgrade():
    """升级数据库结构"""
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'desensitization_tasks' 
            AND COLUMN_NAME = 'report_path'
        """))
        
        exists = result.scalar() > 0
        
        if not exists:
            print("添加 report_path 字段到 desensitization_tasks 表...")
            conn.execute(text("""
                ALTER TABLE desensitization_tasks 
                ADD COLUMN report_path VARCHAR(500) COMMENT '报告文件路径'
            """))
            conn.commit()
            print("✓ report_path 字段添加成功")
        else:
            print("✓ report_path 字段已存在，跳过")

if __name__ == "__main__":
    upgrade()
    print("数据库迁移完成！")

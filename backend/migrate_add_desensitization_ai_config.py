"""
为ai_desensitization_tasks表添加ai_config_id字段
用于支持脱敏任务选择特定的AI模型配置
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine
from sqlalchemy import text

def add_ai_config_id_column():
    """添加ai_config_id字段到ai_desensitization_tasks表"""
    try:
        with engine.connect() as conn:
            # 检查字段是否已存在
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'ai_desensitization_tasks'
                AND COLUMN_NAME = 'ai_config_id'
            """))
            
            column_exists = result.scalar() > 0
            
            if column_exists:
                print("✓ ai_config_id 字段已存在，无需添加")
                return True
            
            # 添加字段
            conn.execute(text("""
                ALTER TABLE ai_desensitization_tasks 
                ADD COLUMN ai_config_id INT NULL COMMENT '使用的AI配置ID，为空则使用默认配置'
            """))
            
            conn.commit()
            print("✓ 成功添加 ai_config_id 字段到 ai_desensitization_tasks 表")
            return True
            
    except Exception as e:
        print(f"✗ 添加字段失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始迁移：为脱敏任务表添加AI配置ID字段...")
    success = add_ai_config_id_column()
    if success:
        print("迁移完成！")
    else:
        print("迁移失败！")
        sys.exit(1)

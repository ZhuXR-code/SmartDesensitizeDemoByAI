"""
数据库迁移脚本：添加 desensitization_method 字段
"""
import sys
sys.path.insert(0, '.')

from app.db.database import engine
from sqlalchemy import text

def add_desensitization_method_column():
    """添加 desensitization_method 字段到 desensitization_rules 表"""
    
    print("开始数据库迁移...")
    
    try:
        with engine.connect() as conn:
            # 检查字段是否已存在
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'desensitization_rules'
                AND COLUMN_NAME = 'desensitization_method'
            """))
            
            column_exists = result.scalar() > 0
            
            if column_exists:
                print("✓ desensitization_method 字段已存在，跳过迁移")
                return
            
            # 添加字段
            print("正在添加 desensitization_method 字段...")
            conn.execute(text("""
                ALTER TABLE desensitization_rules 
                ADD COLUMN desensitization_method VARCHAR(50) NULL
                AFTER category
            """))
            conn.commit()
            
            print("✅ desensitization_method 字段添加成功！")
            
            # 更新现有内置规则的 desensitization_method 字段
            print("正在更新现有规则的 desensitization_method 字段...")
            
            update_rules = [
                (1, 'full_mask'),
                (2, 'simulation'),
                (3, 'simulation'),
                (4, 'simulation'),
                (5, 'simulation'),
                (6, 'simulation'),
                (7, 'simulation'),
                (8, 'simulation'),
                (9, 'simulation'),
                (10, 'simulation'),
                (11, 'simulation'),
                (12, 'simulation'),
                (13, 'partial_mask'),
                (14, 'partial_mask'),
                (15, 'partial_mask'),
                (16, 'partial_mask'),
                (17, 'partial_mask'),
                (18, 'partial_mask'),
                (19, 'partial_mask'),
                (20, 'partial_mask'),
                (21, 'partial_mask'),
            ]
            
            for rule_id, method in update_rules:
                conn.execute(text("""
                    UPDATE desensitization_rules 
                    SET desensitization_method = :method 
                    WHERE id = :id
                """), {"method": method, "id": rule_id})
            
            conn.commit()
            print(f"✅ 已更新 {len(update_rules)} 个规则的 desensitization_method 字段")
            
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 数据库迁移完成！")
    return True

if __name__ == "__main__":
    success = add_desensitization_method_column()
    if success:
        print("\n请运行以下命令更新规则数据：")
        print("python update_desensitization_rules.py")

"""
数据库迁移脚本：添加纯脱敏文件路径字段
执行时间: 2026-05-18
"""
import pymysql
import sys

def migrate():
    try:
        # 连接数据库
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='ai_data_security',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'ai_desensitization_tasks' 
            AND column_name = 'output_file_pure_path'
            AND table_schema = 'ai_data_security'
        """)
        
        exists = cursor.fetchone()[0]
        
        if exists > 0:
            print("✓ 字段 output_file_pure_path 已存在，无需迁移")
            return
        
        # 添加新字段
        print("正在添加 output_file_pure_path 字段...")
        cursor.execute("""
            ALTER TABLE ai_desensitization_tasks 
            ADD COLUMN output_file_pure_path VARCHAR(500) DEFAULT '' COMMENT '纯脱敏文件路径'
        """)
        
        conn.commit()
        
        # 验证字段是否添加成功
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length, column_comment
            FROM information_schema.columns
            WHERE table_name = 'ai_desensitization_tasks'
            AND column_name = 'output_file_pure_path'
            AND table_schema = 'ai_data_security'
        """)
        
        result = cursor.fetchone()
        print(f"✓ 字段添加成功: {result}")
        
        cursor.close()
        conn.close()
        
        print("✓ 数据库迁移完成！")
        
    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    migrate()

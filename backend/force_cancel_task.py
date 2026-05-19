"""
紧急修复脚本 - 强制取消卡住的任务
使用方法: python force_cancel_task.py <task_name>
例如: python force_cancel_task.py "001-不联-不联"
"""
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings
from datetime import datetime

def force_cancel_task(task_name: str):
    """强制取消指定名称的任务"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # 查找任务
        result = conn.execute(text("""
            SELECT id, status, name 
            FROM ai_detection_tasks 
            WHERE name = :task_name
        """), {"task_name": task_name})
        
        row = result.fetchone()
        
        if not row:
            print(f"❌ 未找到任务: {task_name}")
            return
        
        task_id, current_status, name = row
        print(f"找到任务:")
        print(f"  ID: {task_id}")
        print(f"  名称: {name}")
        print(f"  当前状态: {current_status}")
        
        if current_status == 'cancelled':
            print("✓ 任务已经是已取消状态")
            return
        
        if current_status != 'running':
            print(f"⚠️  警告: 任务状态为 {current_status}，不是 running 状态")
            response = input("是否仍然强制设置为 cancelled? (y/n): ")
            if response.lower() != 'y':
                print("已取消操作")
                return
        
        # 更新任务状态
        conn.execute(text("""
            UPDATE ai_detection_tasks 
            SET status = 'cancelled',
                completed_at = :completed_at
            WHERE id = :task_id
        """), {
            "task_id": task_id,
            "completed_at": datetime.now()
        })
        
        conn.commit()
        print(f"\n✅ 任务已成功取消!")
        print(f"   任务ID: {task_id}")
        print(f"   任务名称: {name}")
        print(f"   新状态: cancelled")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python force_cancel_task.py <任务名称>")
        print("例如: python force_cancel_task.py \"001-不联-不联\"")
        sys.exit(1)
    
    task_name = sys.argv[1]
    force_cancel_task(task_name)

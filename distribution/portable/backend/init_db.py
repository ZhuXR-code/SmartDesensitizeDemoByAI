"""
便携版数据库初始化脚本（SQLite）
在首次启动时自动创建数据库和表结构，无需手动安装 MySQL
"""
import os
import sys

# 将后端项目根目录加入 sys.path
BACKEND_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')
if os.path.exists(BACKEND_DIR):
    sys.path.insert(0, os.path.abspath(BACKEND_DIR))
else:
    # 如果是从 distribution/portable 目录运行
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

# 设置环境变量，使用 SQLite
os.environ['DATABASE_URL'] = 'sqlite:///./data/desensitization.db'
os.environ['USE_SQLITE'] = 'true'
os.environ['UPLOAD_DIR'] = './uploads'

from app.db.database import engine, Base
from app.models import detection, desensitization, dataset, report, user, ai

def init():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)
    
    print("[SQLite] 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("[SQLite] 数据库初始化完成！")

if __name__ == '__main__':
    init()

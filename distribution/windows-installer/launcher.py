"""
敏感信息脱敏平台 - 集成启动器
用于 PyInstaller 打包，将所有服务合并为一个可执行文件
"""
import os
import sys
import webbrowser
import threading
import time
import uvicorn

def start_browser():
    time.sleep(3)
    webbrowser.open('http://localhost:5173')

def main():
    os.environ['USE_SQLITE'] = 'true'
    os.environ['DATABASE_URL'] = 'sqlite:///./data/desensitization.db'
    
    data_dir = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), 'data')
    uploads_dir = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), 'uploads')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)
    
    threading.Thread(target=start_browser, daemon=True).start()
    
    print("=" * 50)
    print("  敏感信息智能脱敏平台")
    print("=" * 50)
    print()
    print("  服务启动中...")
    print("  浏览器将自动打开 http://localhost:5173")
    print()
    print("  按 Ctrl+C 停止服务")
    print("=" * 50)
    print()
    
    sys.argv = ['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '5173']
    uvicorn.run('app.main:app', host='0.0.0.0', port=5173)

if __name__ == '__main__':
    main()

@echo off
chcp 65001 >nul
title 敏感信息智能脱敏平台 - 便携式启动

echo ============================================
echo   敏感信息智能脱敏平台 - 便携式启动
echo ============================================
echo.

cd /d "%~dp0"

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo.
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM 设置阿里云 pip 镜像源
set PIP_MIRROR=-i https://mirrors.aliyun.com/pypi/simple/
set PIP_TRUSTED=--trusted-host mirrors.aliyun.com

REM 检查是否已安装依赖
if not exist "backend\.venv" (
    echo [1/4] 创建虚拟环境...
    python -m venv backend\.venv
)

echo [2/4] 安装依赖（使用阿里云镜像加速）...
call backend\.venv\Scripts\pip.exe install %PIP_MIRROR% %PIP_TRUSTED% -r backend\requirements.txt -q
if %errorlevel% neq 0 (
    echo [警告] 阿里云镜像安装失败，尝试默认源...
    call backend\.venv\Scripts\pip.exe install -r backend\requirements.txt -q
)

echo [3/4] 初始化数据库...
call backend\.venv\Scripts\python.exe backend\init_db.py

echo [4/4] 启动服务...
echo.
echo 服务启动中，请稍候...
echo 浏览器将自动打开 http://localhost:5173
echo.
echo 按 Ctrl+C 可停止服务
echo.

start http://localhost:5173
call backend\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 5173

pause

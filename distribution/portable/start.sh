#!/bin/bash

# 敏感信息智能脱敏平台 - 便携式启动脚本 (Linux/Mac)
# 使用阿里云 pip 镜像加速

set -e

cd "$(dirname "$0")"

echo "============================================"
echo "  敏感信息智能脱敏平台 - 便携式启动"
echo "============================================"
echo ""

# 检查 Python
PYTHON=""
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "[错误] 未检测到 Python，请先安装 Python 3.10+"
    exit 1
fi

# 阿里云 pip 镜像
PIP_MIRROR="-i https://mirrors.aliyun.com/pypi/simple/"
PIP_TRUSTED="--trusted-host mirrors.aliyun.com"

echo "[1/4] 创建虚拟环境..."
$PYTHON -m venv backend/.venv

echo "[2/4] 安装依赖（使用阿里云镜像加速）..."
backend/.venv/bin/pip install $PIP_MIRROR $PIP_TRUSTED -r backend/requirements.txt -q || {
    echo "[警告] 阿里云镜像安装失败，尝试默认源..."
    backend/.venv/bin/pip install -r backend/requirements.txt -q
}

echo "[3/4] 初始化数据库..."
backend/.venv/bin/python backend/init_db.py

echo "[4/4] 启动服务..."
echo ""
echo "服务启动中，请稍候..."
echo "浏览器将自动打开 http://localhost:5173"
echo ""
echo "按 Ctrl+C 可停止服务"
echo ""

# 自动打开浏览器
case "$(uname -s)" in
    Darwin) open http://localhost:5173 ;;
    Linux)  xdg-open http://localhost:5173 2>/dev/null || true ;;
esac

backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 5173

#!/bin/bash

# 敏感信息智能脱敏平台 - Docker一键部署脚本 (Linux/Mac)
# 使用阿里云 Docker 镜像加速

set -e

echo "============================================"
echo "  敏感信息智能脱敏平台 - Docker一键部署"
echo "============================================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "[错误] 未检测到 Docker，请先安装 Docker"
    echo "  安装指南: https://docs.docker.com/get-docker/"
    echo "  国内加速: https://developer.aliyun.com/article/688681"
    exit 1
fi

# 检查 Docker Compose
DOCKER_COMPOSE="docker compose"
if ! docker compose version &> /dev/null; then
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        echo "[错误] 未检测到 Docker Compose"
        exit 1
    fi
fi

echo "[1/5] 检测 Docker 环境... ✓"

# 配置阿里云 Docker 镜像加速器
echo "[2/5] 配置阿里云 Docker 镜像加速..."
DOCKER_CONFIG_DIR="$HOME/.docker"
mkdir -p "$DOCKER_CONFIG_DIR"

if [ -f "$DOCKER_CONFIG_DIR/daemon.json" ]; then
    if grep -q "registry-mirrors" "$DOCKER_CONFIG_DIR/daemon.json" 2>/dev/null; then
        echo "  镜像加速器已配置，跳过"
    else
        echo "  检测到 daemon.json 但没有镜像加速配置，请手动添加阿里云镜像加速"
        echo "  参考: https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors"
    fi
else
    cat > "$DOCKER_CONFIG_DIR/daemon.json" <<EOF
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
EOF
    echo "  已配置阿里云 + 腾讯云 + 中科大 Docker 镜像加速"
fi

echo "[3/5] 拉取镜像并构建服务（首次约5-10分钟）..."
echo ""

# 使用 docker compose 或 docker-compose
$DOCKER_COMPOSE up -d --build

echo ""
echo "[4/5] 等待服务启动..."
sleep 10

echo "[5/5] 启动完成！"
echo ""
echo "============================================"
echo "  部署成功！"
echo ""
echo "  访问地址: http://localhost:8080"
echo "  API文档:  http://localhost:8000/api/docs"
echo ""
echo "  数据库信息:"
echo "    地址: localhost:3308"
echo "    用户: root"
echo "    密码: msps"
echo "    库名: desensitization2"
echo ""
echo "  常用命令:"
echo "    停止服务: $DOCKER_COMPOSE down"
echo "    查看日志: $DOCKER_COMPOSE logs -f"
echo "    重启服务: $DOCKER_COMPOSE restart"
echo "============================================"
echo ""

# 尝试自动打开浏览器
case "$(uname -s)" in
    Darwin) open http://localhost:8080 ;;
    Linux)  xdg-open http://localhost:8080 2>/dev/null || true ;;
esac

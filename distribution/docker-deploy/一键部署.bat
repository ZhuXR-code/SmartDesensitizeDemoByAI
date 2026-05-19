@echo off
chcp 65001 >nul
title 敏感信息智能脱敏平台 - Docker一键部署

echo ============================================
echo   敏感信息智能脱敏平台 - Docker一键部署
echo ============================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Docker，请先安装 Docker Desktop
    echo.
    echo 下载地址: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

REM 检查 Docker Compose
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Docker Compose
    pause
    exit /b 1
)

echo [1/5] 检测 Docker 环境... ✓

REM 配置阿里云 Docker 镜像加速器
echo [2/5] 配置阿里云 Docker 镜像加速...
set DOCKER_CONFIG_DIR=%USERPROFILE%\.docker
if not exist "%DOCKER_CONFIG_DIR%" mkdir "%DOCKER_CONFIG_DIR%"

if exist "%DOCKER_CONFIG_DIR%\daemon.json" (
    findstr "registry-mirrors" "%DOCKER_CONFIG_DIR%\daemon.json" >nul
    if %errorlevel% neq 0 (
        echo 检测到 daemon.json 但没有镜像加速配置，准备添加...
    ) else (
        echo 镜像加速器已配置，跳过
    )
) else (
    echo {"registry-mirrors":["https://registry.cn-hangzhou.aliyuncs.com","https://mirror.ccs.tencentyun.com"]} > "%DOCKER_CONFIG_DIR%\daemon.json"
    echo 已配置阿里云 + 腾讯云 Docker 镜像加速
)

echo [3/5] 拉取镜像并构建服务（首次约5-10分钟）...
echo.

docker compose up -d --build

if %errorlevel% neq 0 (
    echo.
    echo [错误] 部署失败，请检查日志
    echo 尝试手动排查：
    echo   1. docker compose logs -f  查看详细日志
    echo   2. 检查网络连接，确保可以访问 Docker Hub
    pause
    exit /b 1
)

echo.
echo [4/5] 等待服务启动...
timeout /t 10 /nobreak >nul

echo [5/5] 启动完成！
echo.
echo ============================================
echo   部署成功！
echo.
echo   访问地址: http://localhost:8080
echo   API文档:  http://localhost:8000/api/docs
echo.
echo   数据库信息:
echo     地址: localhost:3308
echo     用户: root
echo     密码: msps
echo     库名: desensitization2
echo.
echo   常用命令:
echo     停止服务: docker compose down
echo     查看日志: docker compose logs -f
echo     重启服务: docker compose restart
echo ============================================
echo.
echo 按任意键打开浏览器...
pause >nul
start http://localhost:8080

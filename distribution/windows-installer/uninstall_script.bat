@echo off
chcp 65001 >nul
title 卸载敏感信息智能脱敏平台 - 清理数据

echo ============================================
echo   敏感信息智能脱敏平台 - 卸载清理
echo ============================================
echo.

REM 获取当前目录（即安装目录）
set INSTALL_DIR=%~dp0

echo 正在停止正在运行的服务...

REM 尝试停止 Docker 容器（如果存在）
docker ps 2>nul | findstr "desensitization" >nul
if %errorlevel% equ 0 (
    echo [1/3] 停止 Docker 容器...
    cd /d "%INSTALL_DIR%docker-deploy"
    docker compose down 2>nul
    echo   - Docker 容器已停止
) else (
    echo [1/3] 未检测到运行中的 Docker 容器，跳过
)

REM 询问是否删除数据
echo.
echo ┌─────────────────────────────────────┐
echo │  是否保留数据文件（供以后重新安装使用）?  │
echo │                                      │
echo │  选「是」= 保留 data/ uploads/ 目录      │
echo │  选「否」= 全部删除                    │
echo └─────────────────────────────────────┘
echo.

set KEEP_DATA=Y
set /p KEEP_DATA="是否保留数据文件？(Y/N，默认Y): "

if /i "%KEEP_DATA%"=="N" (
    echo [2/3] 删除数据文件...
    if exist "%INSTALL_DIR%data" (
        rmdir /s /q "%INSTALL_DIR%data" 2>nul
        echo   - data/ 已删除
    )
    if exist "%INSTALL_DIR%uploads" (
        rmdir /s /q "%INSTALL_DIR%uploads" 2>nul
        echo   - uploads/ 已删除
    )
    if exist "%INSTALL_DIR%portable\backend\.venv" (
        rmdir /s /q "%INSTALL_DIR%portable\backend\.venv" 2>nul
        echo   - Python 虚拟环境已删除
    )
    echo   - 数据文件已全部清理
) else (
    echo [2/3] 保留数据文件 ✓
)

echo [3/3] 卸载完成！
echo.
echo 安装目录中的其余文件将由 Windows 安装程序自动删除。
echo.
timeout /t 3 /nobreak >nul

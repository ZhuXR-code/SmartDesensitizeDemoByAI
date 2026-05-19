@echo off
chcp 65001 >nul
title 敏感信息脱敏平台 - Windows 安装包构建工具

echo ============================================
echo   敏感信息脱敏平台 - Windows 安装包构建
echo ============================================
echo.

cd /d "%~dp0"

echo 请选择构建方式:
echo.
echo   [1] Inno Setup 安装程序（推荐）
echo       - 支持选择安装目录
echo       - 支持控制面板卸载
echo       - 创建桌面快捷方式
echo       - 需要安装 Inno Setup 编译器
echo       下载: https://jrsoftware.org/isdl.php
echo.
echo   [2] 便携式部署包（文件夹打包）
echo       - 打包成压缩包，解压即用
echo       - 用户需自行安装 Python 3.10+
echo.
echo   [3] PyInstaller 单文件包
echo       - 完全无需任何环境
echo       - 打包为单个 exe 文件
echo       - 适合分发给非技术用户
echo.

set /p CHOICE="请输入选项 (1/2/3): "

if "%CHOICE%"=="1" goto build_innosetup
if "%CHOICE%"=="2" goto build_portable
if "%CHOICE%"=="3" goto build_pyinstaller
echo 无效选项，退出
pause
exit /b 1

:build_innosetup
echo.
echo [构建 Inno Setup 安装程序]...
echo.

REM 检查 Inno Setup 是否安装
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    echo.
    echo [错误] 未找到 Inno Setup 编译器
    echo.
    echo 请先下载安装 Inno Setup:
    echo   https://jrsoftware.org/isdl.php
    echo.
    echo 安装后，也可以手动编译:
    echo   右键 setup.iss -^> 选择 "Compile"
    echo.
    pause
    exit /b 1
)

%ISCC% setup.iss
if %errorlevel% equ 0 (
    echo.
    echo 安装程序构建成功！
    echo 输出文件: ..\..\dist\installer\敏感信息脱敏平台_Setup.exe
    echo.
    echo 用户双击运行即可安装，支持:
    echo   - 选择安装目录
    echo   - 创建桌面快捷方式
    echo   - 控制面板卸载
) else (
    echo.
    echo [错误] 构建失败，请检查 Inno Setup 配置
)
pause
exit /b 0

:build_portable
echo.
echo [构建便携式部署包]...
echo.

set OUTPUT_DIR=..\..\dist\portable
set OUTPUT_FILE=..\..\dist\敏感信息脱敏平台_便携版.zip
mkdir "%OUTPUT_DIR%" 2>nul

REM 复制便携式文件
xcopy /E /I /Y ..\portable "%OUTPUT_DIR%\" >nul
xcopy /E /I /Y ..\docker-deploy "%OUTPUT_DIR%\docker-deploy\" >nul

REM 如果存在 7z，用 7z 打包
set ZIPPER=""
where 7z >nul 2>&1 && set ZIPPER=7z

if defined ZIPPER (
    7z a -r "%OUTPUT_FILE%" "%OUTPUT_DIR%\*" >nul
    echo 便携式部署包已生成: %OUTPUT_FILE%
) else (
    echo 便携式部署包已生成到: %OUTPUT_DIR%
    echo.
    echo 如需打包为 zip，请安装 7-Zip 或手动压缩该目录
)

echo.
echo 使用方法:
echo   用户解压后，双击 启动平台.bat 即可
echo.
pause
exit /b 0

:build_pyinstaller
echo.
echo [构建 PyInstaller 单文件包]...
echo.

REM 检查开发环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 需要 Python 环境来执行打包
    pause
    exit /b 1
)

set OUTPUT_DIR=..\..\dist\pyinstaller
mkdir "%OUTPUT_DIR%" 2>nul

pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com pyinstaller -q

REM 构建后端单文件
pyinstaller --onefile --name "敏感信息脱敏平台" ^
    --add-data "..\..\backend;backend" ^
    --hidden-import uvicorn ^
    --hidden-import sqlalchemy ^
    ..\launcher.py ^
    --distpath "%OUTPUT_DIR%"

echo.
echo PyInstaller 单文件包已生成到: %OUTPUT_DIR%
echo.
pause
exit /b 0

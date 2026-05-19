# Windows 一键安装包

## 快速使用

### 方案一：下载预构建安装包

从发布页面下载 `敏感信息脱敏平台_Setup.exe`，双击运行，按提示完成安装。

安装完成后，桌面会自动生成快捷方式，双击即可启动平台。

### 方案二：自行构建

如果你有开发环境，可以自行构建安装包：

```bash
# 1. 安装依赖
pip install pyinstaller

# 2. 运行构建脚本
build_installer.bat

# 3. 选择 [3] PyInstaller 单文件包
```

构建完成后，`dist/pyinstaller/敏感信息脱敏平台.exe` 即为单文件可执行程序。

## 系统要求

- **Windows 10/11** 64位
- 无需 Python、npm、MySQL 环境
- 无需网络连接（离线可用）

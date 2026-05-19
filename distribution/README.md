# 敏感信息智能脱敏平台 — 安装包

> 本目录包含平台的多种部署方案，面向不同技术背景的用户。

---

## 快速选择

| 你的情况 | 推荐方案 | 难度 |
|---------|---------|------|
| 已安装 Docker | [Docker 一键部署](#方案一-docker-一键部署推荐) | ⭐ |
| 有 Python 基础，无 Docker | [便携式部署](#方案二-便携式部署-sqlite) | ⭐⭐ |
| 无任何环境（Windows） | [Windows 安装包](#方案三-windows-安装包) | ⭐ |

---

## 目录结构

```
distribution/
├── README.md                         ← 本文件
├── 安装说明.md                   ← 快速入门指南
│
├── docker-deploy/                    ← Docker 一键部署方案（推荐）
│   ├── 一键部署.bat              ← Windows 一键启动（双击即可）
│   ├── deploy.sh                     ← Linux/Mac 一键启动
│   ├── docker-compose.yml            ← 服务编排配置
│   └── README.md                     ← Docker 部署说明
│
├── portable/                         ← 便携式部署方案（SQLite，无需 MySQL）
│   ├── 启动平台.bat              ← Windows 启动脚本
│   ├── start.sh                      ← Linux/Mac 启动脚本
│   ├── backend/                      ← 后端初始化脚本和配置
│   │   ├── init_db.py                ← SQLite 数据库自动初始化
│   │   └── requirements.txt          ← Python 依赖清单
│   └── README.md                     ← 便携式部署说明
│
├── windows-installer/                ← Windows 安装包
│   ├── README.md                     ← Windows 安装说明
│   ├── build_installer.bat           ← 安装包构建脚本
│   └── launcher.py                   ← 集成启动器（PyInstaller）
│
└── 部署说明.md                   ← 详细部署文档
```

---

## 方案一：Docker 一键部署（推荐）

> 需要安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。

```bash
cd docker-deploy

# Windows（双击 一键部署.bat 或运行）
一键部署.bat

# Linux/Mac
chmod +x deploy.sh && ./deploy.sh
```

启动后浏览器访问：**http://localhost:8080**

---

## 方案二：便携式部署（SQLite）

> 需要安装 Python 3.10+

```bash
cd portable

# 首次使用
pip install -r requirements.txt

# Windows（双击 启动平台.bat）
启动平台.bat

# Linux/Mac
chmod +x start.sh && ./start.sh
```

启动后浏览器访问：**http://localhost:5173**

---

## 方案三：Windows 安装包

> 适合完全不熟悉技术的用户，无需安装任何环境。

详见 [windows-installer/README.md](windows-installer/README.md)

### 预构建安装包

从 Release 页面下载 `敏感信息脱敏平台_Setup.exe`，双击安装即可。

### 自行构建

如果你有 Python 开发环境，可运行构建脚本生成单文件 exe：

```bash
cd windows-installer
build_installer.bat
# 选择 [3] PyInstaller 单文件包
```

构建完成后，可执行文件将在 `dist/pyinstaller/` 目录下生成。

---

## 对比

| 方案 | 环境要求 | 适用场景 | 适用人群 |
|------|---------|---------|---------|
| Docker 部署 | Docker Desktop | 企业正式部署 | IT 人员、运维 |
| 便携式部署 | Python 3.10+ | 个人使用/开发测试 | 有编程基础的用户 |
| Windows 安装包 | 无 | 小白用户快速使用 | 所有用户 |

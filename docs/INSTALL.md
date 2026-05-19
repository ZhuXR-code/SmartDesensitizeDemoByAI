# 敏感信息脱敏平台 — 安装部署手册

## 目录

1. [系统要求](#1-系统要求)
2. [项目结构](#2-项目结构)
3. [环境依赖](#3-环境依赖)
4. [一键部署方案（推荐）](#4-一键部署方案推荐)
5. [快速安装](#5-快速安装)
6. [手动安装](#6-手动安装)
7. [数据库初始化](#7-数据库初始化)
8. [启动服务](#8-启动服务)
9. [验证安装](#9-验证安装)
10. [国内镜像加速](#10-国内镜像加速)
11. [常见问题](#11-常见问题)
12. [Docker 部署](#12-docker-部署)

---

## 1. 系统要求

| 项目 | 最低配置 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 10 / Ubuntu 20.04 / macOS 12 | Windows 11 / Ubuntu 22.04 |
| CPU | 2 核 | 4 核以上 |
| 内存 | 4GB | 8GB 以上 |
| 磁盘 | 10GB | 50GB（含数据存储） |
| Node.js | v18.x | v20.x |
| Python | 3.10+ | 3.11+ |
| MySQL | 8.0+ | 8.0+ |

---

## 2. 项目结构

```
code03/
├── backend/                    # 后端服务（FastAPI）
│   ├── app/                    # 应用代码
│   │   ├── api/                # API 路由（含 AI 智能模块）
│   │   ├── core/               # 配置与日志
│   │   ├── db/                 # 数据库连接
│   │   ├── models/             # 数据模型（含 AI 配置/识别/复核）
│   │   ├── schemas/            # Pydantic 校验
│   │   └── services/           # 业务逻辑（含 AI 推理服务）
│   ├── requirements.txt        # Python 依赖
│   ├── run.py                  # 启动入口
│   └── init_db.sql             # 数据库建库脚本
├── frontend/                   # 前端（Vue 3）
│   ├── src/
│   │   ├── api/                # API 调用（含 AI 接口）
│   │   ├── components/         # 公共组件
│   │   ├── router/             # 路由
│   │   ├── stores/             # 状态管理
│   │   ├── styles/             # 主题样式
│   │   ├── themes/             # 四套风格组件（经典/Vue经典/暗紫/黑金）
│   │   └── views/              # 页面（含 AI 智能页面）
│   ├── package.json
│   └── vue.config.js
├── uploads/                    # 上传文件存储
├── docs/                       # 文档
├── deploy/                     # 数据库初始化脚本
└── distribution/               # 一键部署安装包
    ├── docker-deploy/          # Docker 一键部署方案
    ├── portable/               # 便携式部署方案（SQLite）
    ├── windows-installer/      # Windows 安装包
    ├── README.md               # 部署方案总览
    ├── 安装说明.md             # 快速入门指南
    └── 部署说明.md             # 详细部署文档
```

---

## 3. 环境依赖

### 3.1 后端依赖（Python）

```
fastapi==0.109.2              # Web 框架
uvicorn[standard]==0.27.1     # ASGI 服务器
sqlalchemy==2.0.27            # ORM
pymysql==1.1.0                # MySQL 驱动
pydantic==2.6.1               # 数据校验
pydantic-settings==2.1.0      # 配置管理
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4        # 密码加密
openpyxl==3.1.2               # Excel 解析
pandas==2.2.0                 # 数据处理
langdetect==1.0.9             # 语言检测
python-magic==0.4.27          # 文件类型检测
chardet==5.2.0                # 编码检测
aiofiles==23.2.1              # 异步文件
httpx==0.26.0                 # HTTP 客户端（LLM API 调用）
numpy==1.26.4                 # 数值计算
cryptography==42.0.2          # 加密库（密钥管理）
weasyprint==60.2              # HTML 报告生成
```

> 💡 **AI 模块说明**：AI 智能识别与脱敏功能通过 `httpx` 调用各大模型的 HTTP API 实现，无需额外安装 langchain、openai 等重量级 SDK，保持依赖精简。

### 3.2 前端依赖（Node.js）

```
vue@^3.4.15                  # 前端框架
vue-router@^4.2.5            # 路由
pinia@^2.1.7                 # 状态管理
element-plus@^2.5.3          # UI 组件库
@element-plus/icons-vue      # 图标库
axios@^1.6.7                 # HTTP 请求
echarts@^5.4.3               # 图表
sass@^1.70.0                 # CSS 预处理器
```

---

## 4. 一键部署方案（推荐）

> 🎯 面向不同技术背景的用户，提供三种一键部署方式。所有安装包位于 `distribution/` 目录。

| 你的情况 | 推荐方案 | 难度 | 前置要求 |
|---------|---------|------|---------|
| 已安装 Docker | [Docker 一键部署](#41-docker-一键部署) | ⭐ | Docker Desktop |
| 有 Python，无 Docker/MySQL | [便携式部署](#42-便携式部署-sqlite) | ⭐⭐ | Python 3.10+ |
| 纯 Windows 小白用户 | [Windows 安装包](#43-windows-安装包) | ⭐ | 无 |

### 4.1 Docker 一键部署

> 适合大部分用户，只需安装 Docker Desktop 即可。自动部署前端、后端、MySQL 数据库全套服务。

**第1步：安装 Docker Desktop**

下载并安装 Docker Desktop：https://www.docker.com/products/docker-desktop/

安装后重启电脑，确保 Docker 图标在任务栏显示。

**第2步：一键启动**

进入 `distribution/docker-deploy` 目录：

- **Windows**：双击 `一键部署.bat`（已配置阿里云 Docker 镜像加速）
- **Linux/Mac**：运行 `chmod +x deploy.sh && ./deploy.sh`

部署脚本会自动完成：拉取镜像 → 创建容器 → 初始化数据库 → 启动全部服务

**第3步：访问平台**

打开浏览器访问：**http://localhost:8080**

默认管理员账号：`admin` / 密码：`admin123`

**服务端口：**
- 前端页面：`8080`
- 后端 API：`8000`
- MySQL 数据库：`3308`

**卸载/删除：**
```bash
cd distribution/docker-deploy

# 停止并删除容器（保留数据卷）
docker compose down

# 停止并删除容器+数据卷（完全清除）
docker compose down -v
```

### 4.2 便携式部署（SQLite）

> 无需安装 MySQL 和 Docker，使用 SQLite 作为数据库，适合个人使用和小型团队。

**第1步：安装 Python**

下载安装 Python 3.10+：https://www.python.org/downloads/

安装时**务必勾选** "Add Python to PATH"。

**第2步：安装依赖（首次使用）**

```bash
cd distribution/portable/backend

# 使用阿里云镜像加速（推荐）
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

**第3步：启动平台**

- **Windows**：双击 `distribution/portable/启动平台.bat`
- **Linux/Mac**：运行 `chmod +x distribution/portable/start.sh && ./distribution/portable/start.sh`

首次启动会自动初始化 SQLite 数据库和表结构。

**第4步：访问平台**

打开浏览器访问：**http://localhost:5173**

**卸载/删除：**
直接删除 `distribution/portable/` 目录即可。数据文件存储在 `portable/backend/data/` 中。

### 4.3 Windows 安装包

> 适合完全不熟悉技术的 Windows 用户。安装后像普通软件一样使用，可选择安装目录，提供卸载程序。

**安装步骤：**

1. 从发布页面下载 `敏感信息脱敏平台_Setup.exe`
2. 双击运行安装向导
3. 选择安装目录（默认 `C:\Program Files\SensitiveDataPlatform`）
4. 勾选"创建桌面快捷方式"
5. 点击"安装"，等待完成

**使用方式：**

双击桌面快捷方式，等待服务启动后自动打开浏览器访问平台。

**卸载方式：**
- 方式一：开始菜单 → 敏感信息脱敏平台 → 卸载
- 方式二：控制面板 → 程序和功能 → 右键卸载
- 方式三：运行安装目录下的 `uninstall.exe`

**安装包构建（开发者）：**

如需重新构建安装包：
```bash
cd distribution/windows-installer

# 安装 Inno Setup 6（https://jrsoftware.org/isinfo.php）

# 运行构建脚本
build_installer.bat
```

> 💡 构建需要先安装 Inno Setup 6（免费软件）。构建脚本会自动打包 Python 运行时和前端构建产物。

---

## 5. 快速安装

### 5.1 安装 MySQL

**方式一：免安装 MySQL 镜像（推荐，一键启动）**

下载并运行本项目提供的 MySQL Docker 镜像：

```bash
cd deploy
docker-compose up -d mysql
```

这会自动创建一个包含所有表结构和内置规则的数据库 `desensitization2`，端口映射到 `3308`，root 密码为 `msps`。

**方式二：使用 XAMPP / phpStudy**

1. 下载 [XAMPP](https://www.apachefriends.org/) 或 phpStudy
2. 启动 MySQL 服务
3. 创建数据库后执行 [init_db.sql](#63-初始化数据库sql脚本)

**方式三：手动安装 MySQL 8.0**

- [MySQL 官方下载](https://dev.mysql.com/downloads/mysql/)

### 5.2 安装 Python

1. 下载 [Python 3.11+](https://www.python.org/downloads/)
2. 安装时勾选 "Add Python to PATH"
3. 验证：`python --version`

### 5.3 安装 Node.js

1. 下载 [Node.js 20.x LTS](https://nodejs.org/)
2. 验证：`node --version`

### 5.4 一键启动

```bash
# 进入项目根目录
cd code03

# 1. 安装后端依赖并启动
cd backend
pip install -r requirements.txt
python run.py

# 2. 新开终端，安装前端依赖并启动
cd frontend
npm install
npm run serve
```

访问 http://localhost:8080 即可使用。

---

## 6. 手动安装

### 6.1 安装后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# Windows 激活
venv\Scripts\activate

# Linux/macOS 激活
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 6.2 配置数据库连接

编辑 `backend/.env` 文件：

```env
DEBUG=true
DATABASE_URL=mysql+pymysql://root:msps@localhost:3308/desensitization2

MYSQL_HOST=localhost
MYSQL_PORT=3308
MYSQL_USER=root
MYSQL_PASSWORD=msps
MYSQL_DATABASE=desensitization2

UPLOAD_DIR=../uploads
MAX_UPLOAD_SIZE=104857600
LOG_LEVEL=INFO
```

### 6.3 安装前端

```bash
cd frontend
npm install
```

---

## 7. 数据库初始化

### 7.1 创建数据库

```sql
CREATE DATABASE IF NOT EXISTS desensitization2
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

### 7.2 数据库表结构

系统共 **19 张表**，分 6 个模块：

**数据集模块：**
| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `datasets` | 数据集管理 | id, name, file_path, row_count, columns(JSON) |
| `data_sources` | 数据源配置 | id, name, source_type, config(JSON) |

**检测模块：**
| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `detection_tasks` | 识别任务 | id, name, status, progress, found_count |
| `detection_results` | 识别结果 | id, task_id, column_name, rule_name, confidence |
| `detection_rules` | 识别规则 | id, name, language, rule_type, pattern |
| `detection_rule_sets` | 规则集 | id, name, rules(JSON) |

**脱敏模块：**
| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `desensitization_tasks` | 脱敏任务 | id, name, output_mode, key_id, status |
| `desensitization_results` | 脱敏结果 | id, task_id, original_value, desensitized_value |
| `desensitization_rules` | 脱敏规则 | id, name, desensitization_method, category |
| `desensitization_keys` | 脱敏密钥 | id, alias, key_hash |

**报告模块：**
| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `reports` | 报告记录 | id, report_type, summary(JSON), file_path |

**用户模块：**
| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `users` | 用户 | id, username, hashed_password |
| `roles` | 角色 | id, name, permissions |
| `user_role` | 用户角色关联 | user_id, role_id |

### 7.3 初始化数据库 SQL 脚本

完整建表 SQL 由后端 ORM 自动生成，启动时执行：

```bash
cd backend
python -c "from app.db.database import init_db; init_db()"
```

### 7.4 内置数据

系统预置了以下数据：

**脱敏规则（52条）：**
- 遮盖类（8条）：完全遮盖、姓名/手机号/身份证/银行卡/地址/国家/邮箱部分遮盖、通用等长/固定遮盖
- 仿真类（16条）：中/英/日/韩/法/德 六语言姓名+字段仿真
- 关联造数类（16条）：六语言姓名+手机号+邮箱+地址关联造数（确定性脱敏）

**脱敏密钥（30组）：**
- 密钥-01 ~ 密钥-30，用于跨表关联数据一致性脱敏

**规则集（2个）：**
- 001 识别集：综合敏感字段检测
- 002 识别集：专用场景

---

## 8. 启动服务

### 8.1 启动后端

```bash
cd backend
python run.py
```

后端默认端口：`8000`

API 文档地址：http://localhost:8000/api/docs

### 8.2 启动前端

```bash
cd frontend
npm run serve
```

前端默认端口：`8080`

访问地址：http://localhost:8080

### 8.3 启动指定端口

```bash
# 后端
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端（修改 vue.config.js 中的 devServer.port）
```

---

## 9. 验证安装

1. 浏览器打开 http://localhost:8080
2. 进入"数据集管理" → "导入数据"，上传一个 CSV 文件
3. 进入"敏感数据识别" → "创建识别任务"，执行识别
4. 进入"数据脱敏" → "创建脱敏任务"，执行脱敏
5. 进入"运营报表" → "平台运营成效"，查看数据大盘
6. 点击右上角风格切换，验证经典/Vue经典/暗紫/黑金四套风格

---

## 10. 国内镜像加速

> 国内用户在使用 pip、npm、Docker 时可能会遇到下载慢或连接超时的问题，推荐使用以下国内镜像源。

### 10.1 pip 镜像（阿里云）

```bash
# 临时使用
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 永久配置
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

其他可选镜像：
- 清华源：`https://pypi.tuna.tsinghua.edu.cn/simple/`
- 中科大：`https://pypi.mirrors.ustc.edu.cn/simple/`
- 腾讯云：`https://mirrors.cloud.tencent.com/pypi/simple/`

### 10.2 npm 镜像（淘宝）

```bash
# 临时使用
npm install --registry=https://registry.npmmirror.com

# 永久配置
npm config set registry https://registry.npmmirror.com
```

### 10.3 Docker 镜像（阿里云）

Docker Desktop 配置：
1. 打开 Docker Desktop → Settings → Docker Engine
2. 在 `registry-mirrors` 中添加：
```json
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://mirror.ccs.tencentyun.com"
  ]
}
```
3. 点击 "Apply & Restart"

> 💡 `distribution/docker-deploy/一键部署.bat` 已默认配置阿里云 Docker 镜像加速。

---

## 11. 常见问题

### Q: 数据库连接失败

**A:** 检查 MySQL 服务是否启动，端口、用户名、密码是否正确
```bash
# 检查数据库连接
mysql -h localhost -P 3308 -u root -pmsps -e "SELECT 1"
```

### Q: pip install 报错

**A:** 升级 pip 后重试
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Q: npm install 报错

**A:** 使用淘宝镜像
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### Q: 端口被占用

**A:** 释放端口或修改配置
```bash
# Windows 查看端口占用
netstat -ano | findstr :8080

# Linux/macOS
lsof -i :8080
```

---

## 12. Docker 部署（手动方式）

> 如需更简单的 Docker 部署方式，请使用 [4.1 Docker 一键部署](#41-docker-一键部署)。以下为手动 Docker 部署步骤。

项目根目录包含 `docker-compose.yml`，可手动构建和部署：

```bash
cd code03

# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

服务端口映射：
- 前端：`8080:80`
- 后端：`8000:8000`
- 数据库：`3308:3306`

访问 http://localhost:8080

> 💡 推荐使用 `distribution/docker-deploy/` 目录下的脚本，支持国内镜像加速和一键操作。

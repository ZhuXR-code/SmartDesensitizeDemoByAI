# 敏感信息脱敏平台 — 安装部署手册

## 目录

1. [系统要求](#1-系统要求)
2. [项目结构](#2-项目结构)
3. [环境依赖](#3-环境依赖)
4. [快速安装（推荐）](#4-快速安装推荐)
5. [手动安装](#5-手动安装)
6. [数据库初始化](#6-数据库初始化)
7. [启动服务](#7-启动服务)
8. [验证安装](#8-验证安装)
9. [常见问题](#9-常见问题)
10. [Docker 部署](#10-docker-部署)

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
code1-汇总/
├── backend/                    # 后端服务（FastAPI）
│   ├── app/                    # 应用代码
│   │   ├── api/                # API 路由
│   │   ├── core/               # 配置与日志
│   │   ├── db/                 # 数据库连接
│   │   ├── models/             # 数据模型
│   │   ├── schemas/            # Pydantic 校验
│   │   └── services/           # 业务逻辑
│   ├── requirements.txt        # Python 依赖
│   ├── run.py                  # 启动入口
│   └── init_db.sql             # 数据库建库脚本
├── frontend/                   # 前端（Vue 3）
│   ├── src/
│   │   ├── api/                # API 调用
│   │   ├── components/         # 公共组件
│   │   ├── router/             # 路由
│   │   ├── stores/             # 状态管理
│   │   ├── styles/             # 主题样式
│   │   ├── themes/             # 三套风格组件
│   │   └── views/              # 页面
│   ├── package.json
│   └── vue.config.js
├── uploads/                    # 上传文件存储
├── docs/                       # 文档
└── deploy/                     # 部署包
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
httpx==0.26.0                 # HTTP 客户端
```

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

## 4. 快速安装（推荐）

### 4.1 安装 MySQL

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

### 4.2 安装 Python

1. 下载 [Python 3.11+](https://www.python.org/downloads/)
2. 安装时勾选 "Add Python to PATH"
3. 验证：`python --version`

### 4.3 安装 Node.js

1. 下载 [Node.js 20.x LTS](https://nodejs.org/)
2. 验证：`node --version`

### 4.4 一键启动

```bash
# 进入项目根目录
cd code1-汇总

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

## 5. 手动安装

### 5.1 安装后端

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

### 5.2 配置数据库连接

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

### 5.3 安装前端

```bash
cd frontend
npm install
```

---

## 6. 数据库初始化

### 6.1 创建数据库

```sql
CREATE DATABASE IF NOT EXISTS desensitization2
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

### 6.2 数据库表结构

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

### 6.3 初始化数据库 SQL 脚本

完整建表 SQL 由后端 ORM 自动生成，启动时执行：

```bash
cd backend
python -c "from app.db.database import init_db; init_db()"
```

### 6.4 内置数据

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

## 7. 启动服务

### 7.1 启动后端

```bash
cd backend
python run.py
```

后端默认端口：`8000`

API 文档地址：http://localhost:8000/api/docs

### 7.2 启动前端

```bash
cd frontend
npm run serve
```

前端默认端口：`8080`

访问地址：http://localhost:8080

### 7.3 启动指定端口

```bash
# 后端
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端（修改 vue.config.js 中的 devServer.port）
```

---

## 8. 验证安装

1. 浏览器打开 http://localhost:8080
2. 进入"数据集管理" → "导入数据"，上传一个 CSV 文件
3. 进入"敏感数据识别" → "创建识别任务"，执行识别
4. 进入"数据脱敏" → "创建脱敏任务"，执行脱敏
5. 进入"运营报表" → "平台运营成效"，查看数据大盘
6. 点击右上角风格切换，验证经典/暗紫/黑金三套风格

---

## 9. 常见问题

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

## 10. Docker 部署

项目根目录包含 `docker-compose.yml`，一键部署：

```bash
cd code1-汇总

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

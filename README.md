# 敏感信息智能脱敏平台

> **本平台完全由AI生成** | 基于 Vue3 + FastAPI 的敏感信息识别与脱敏通用工具平台

## 项目概述

一款面向企业数据安全管理的**智能敏感信息识别与脱敏平台**，支持多语言（中/英/日/韩/法/德）敏感数据识别、AI大模型智能识别与脱敏、规则引擎识别、多种脱敏策略和报告输出。无需编程基础，普通业务人员即可完成数据安全保护。

## 核心亮点

- **AI大模型驱动**：集成 DeepSeek/OpenAI/千问/Kimi 等大模型，语义级敏感判断
- **双引擎识别**：规则引擎（正则+关键词）+ AI引擎（LLM语义分析），双重保障
- **多语言智能识别**：支持6种语言的敏感数据识别，基于字符集特征自动检测语言
- **识别-脱敏一体化**：识别结果一键跳转脱敏，自动推荐最优脱敏规则
- **关联仿真脱敏**：基于密钥的确定性脱敏，保证跨表数据一致性
- **人工复核机制**：AI识别结果可逐条复核确认，复核结果驱动脱敏
- **可视化前后对比**：脱敏前展示10-20条数据对比，确认后才执行全量处理
- **快速脱敏工作流**：引导式4步操作流程（导入→识别→配置→报告）
- **多种报告格式**：支持HTML在线预览和Markdown格式下载
- **四种页面风格切换**：经典、Vue经典、暗紫、黑金四种主题
- **前后端分离架构**：Vue3 + FastAPI，提供完整RESTful API
- **三套部署方案**：Docker一键部署 / 便携式部署(SQLite) / Windows安装包

## 技术架构

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4 | 前端框架，Composition API |
| Element Plus | ^2.5 | UI 组件库 |
| Pinia | ^2.1 | 状态管理 |
| Vue Router | ^4.2 | SPA 路由 |
| ECharts | ^5.4 | 数据可视化图表 |
| Axios | ^1.6 | HTTP 请求 |
| Sass | ^1.70 | CSS 预处理 |

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.109 | 异步 Web 框架 |
| SQLAlchemy | 2.0 | ORM |
| MySQL 8.0 / SQLite | - | 数据库 |
| Pandas | 2.2 | 数据处理 |
| langdetect | 1.0 | 语言检测 |
| openpyxl | 3.1 | Excel 读写 |
| httpx | 0.26 | LLM API 调用 |

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    前端层 (Vue 3 SPA)                        │
│  首页 │ 数据集 │ 识别 │ 脱敏 │ AI智能 │ 报表 │ 帮助          │
│  4套主题: 经典 / Vue经典 / 暗紫 / 黑金                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP REST API
┌──────────────────────────▼──────────────────────────────────┐
│                   API 网关 (FastAPI)                         │
│  /api/dashboard  /api/datasets  /api/detection              │
│  /api/desensitization  /api/ai  /api/platform-report        │
│  /api/data-sources  /api/reports                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   服务层 (Services)                          │
│  DetectionEngine  DesensitizationEngine  AiService          │
│  LanguageDetector  DeterministicMasking  ReportGenerator    │
│  DataService  DBConnector  TaskManager  AddressParser       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   数据存储层                                  │
│  MySQL 8.0 / SQLite  │  文件系统  │  外部AI API              │
└─────────────────────────────────────────────────────────────┘
```

## 功能模块

### 1. 首页仪表盘
- 核心指标卡片（数据集总数、识别任务数、脱敏任务数、发现敏感数）
- 最近任务列表（识别/脱敏/AI识别/AI脱敏）
- 敏感类型分布图表
- AI任务统计汇总

### 2. 数据集管理
- **文件导入**：支持 Excel/CSV/TXT/JSON/Markdown/日志，拖拽上传，自动识别编码
- **数据库导入**：支持 MySQL/PostgreSQL/Oracle/SQL Server
- **剪贴板粘贴**：从 Excel 复制数据直接粘贴导入
- **数据集管理**：列表/详情/预览/删除
- **数据源配置**：数据库连接信息管理

### 3. 敏感数据识别（规则引擎）
- 内置多语言识别规则（正则+关键词）
- 支持6种语言自动检测（中/英/日/韩/法/德）
- 支持自定义识别规则
- 规则集管理（组合多个规则适应不同场景）
- 实时任务进度和日志
- 识别结果可视化（饼图+柱状图+明细）
- 一键跳转脱敏

### 4. 数据脱敏
- **5种脱敏策略**：完全遮盖、部分遮盖、仿真造数、关联仿真、固定遮盖
- **智能规则推荐**：根据识别结果自动匹配最优脱敏规则
- **预览确认**：执行前展示10-20条脱敏前后对比数据
- **关联仿真**：基于HMAC-SHA256的确定性脱敏，30组密钥业务隔离
- **输出模式**：生成副本 / 覆盖原数据
- **文件下载**：脱敏后数据文件下载

### 5. AI智能模块
- **AI配置管理**：多模型支持（OpenAI/DeepSeek/Qwen/Kimi/GLM/文心/Azure/自定义）
- **AI敏感识别**：基于LLM的语义级敏感判断，法规依据引用，风险等级评估
- **AI脱敏**：遮盖/仿真/关联仿真三种模式，输出格式选择（XLSX/CSV）
- **人工复核**：逐条复核确认，复核统计，复核结果驱动脱敏
- **AI报告**：HTML/Markdown双格式，风险分布可视化
- **联网搜索增强**（可选）
- **DeepSeek思考模式**（可选）

### 6. 报告系统
- 脱敏任务报告（HTML在线预览 / Markdown下载）
- 平台运营报表（领导视图）：6大KPI卡片、8项合规指标、安全保护成效饼图、效率趋势折线图

### 7. 快速脱敏工作流
- 引导式4步操作流程（导入→识别→配置→报告）
- 进度自动跟踪（localStorage持久化）
- 侧边栏"快速脱敏"菜单入口

### 8. 页面风格切换
| 主题 | 特点 | 适合场景 |
|------|------|---------|
| 经典 | 蓝白配色、简洁明快 | 日常办公 |
| Vue经典 | Element Plus 默认风格 | 开发人员 |
| 暗紫 | 暮色紫雾玻璃质感 | 夜间使用 |
| 黑金 | 素雅大地色系 | 正式演示 |

### 9. CLI命令行工具
- 命令行脱敏处理
- 规则模板JSON配置

## 项目结构

```
code03/
├── backend/                    # 后端 FastAPI 项目
│   ├── app/
│   │   ├── api/               # API 路由（含 ai.py）
│   │   ├── core/              # 核心配置（config.py, logger.py）
│   │   ├── db/                # 数据库连接
│   │   ├── models/            # 数据模型（含 ai.py）
│   │   ├── schemas/           # Pydantic 模型（含 ai.py）
│   │   └── services/          # 业务逻辑（含 ai_service.py, task_manager.py）
│   ├── requirements.txt
│   └── run.py
│
├── frontend/                   # 前端 Vue 3 项目
│   ├── src/
│   │   ├── api/               # API 封装（含 ai.js）
│   │   ├── components/        # 公共组件（ThemeLoader, ThemeLayout）
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # 状态管理（theme.js）
│   │   ├── styles/            # 主题样式
│   │   ├── themes/            # 4套主题组件
│   │   │   ├── classic/       # 经典主题
│   │   │   ├── vue-classic/   # Vue经典主题
│   │   │   ├── dark-purple/   # 暗紫主题
│   │   │   └── black-gold/    # 黑金主题
│   │   └── views/             # 页面视图
│   ├── package.json
│   └── vue.config.js
│
├── distribution/               # 安装包文件（面向最终用户）
│   ├── docker-deploy/         # Docker 一键部署方案
│   ├── portable/              # 便携式部署方案（SQLite）
│   ├── windows-installer/     # Windows 安装包
│   ├── README.md              # 安装包总览
│   ├── 安装说明.md            # 快速入门指南
│   └── 部署说明.md            # 详细部署文档
│
├── deploy/                     # Docker 部署配置文件（供开发参考）
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── nginx.conf
│   └── init_db.sql
│
├── cli/                        # CLI 命令行工具
│   ├── desensitize_cli.py
│   └── rules_template.json
│
├── docs/                       # 项目文档
│   ├── PRODUCT_SPEC.md        # 产品需求说明书
│   ├── TECH_DOC.md            # 技术架构文档
│   ├── USER_MANUAL.md         # 用户操作手册
│   ├── API_ADAPTATION_GUIDE.md # API适配说明
│   ├── INSTALL.md             # 安装部署手册
│   ├── PRESENTATION.md        # 项目演示文稿
│   ├── COMPETITION_BROCHURE.md # 产品手册
│   ├── PLATFORM_ANALYSIS.md   # 功能分析报告
│   └── WORKFLOW_DESIGN.md     # 工作流设计方案
│
└── updateLogDoc/               # 开发更新日志
```

## 快速开始

### 方式一：Docker 一键部署（推荐，无需任何环境）

```bash
cd distribution/docker-deploy

# Windows：双击 一键部署.bat
# Linux/Mac：
chmod +x deploy.sh && ./deploy.sh
```

访问 **http://localhost:8080**

### 方式二：便携式部署（需 Python 3.10+）

```bash
cd distribution/portable

# Windows：双击 启动平台.bat
# Linux/Mac：
chmod +x start.sh && ./start.sh
```

访问 **http://localhost:5173**

### 方式三：手动开发环境启动

```bash
# 后端
cd backend
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
python run.py
# => http://localhost:8000  |  API文档: http://localhost:8000/api/docs

# 前端
cd frontend
npm config set registry https://registry.npmmirror.com
npm install
npm run serve
# => http://localhost:8080
```

## 安装包说明

详见 [distribution/README.md](distribution/README.md)，提供三种部署方案：

| 方案 | 前置要求 | 启动方式 | 适用人群 |
|------|---------|---------|---------|
| Docker 部署 | Docker Desktop | 双击 `一键部署.bat` | IT 人员、运维 |
| 便携式部署 | Python 3.10+ | 双击 `启动平台.bat` | 个人使用 |
| Windows 安装包 | 无需环境 | 双击 exe 安装 | 小白用户 |

> 所有脚本已内置阿里云镜像加速，国内用户无需翻墙。

## 相关文档

- [产品需求说明书](docs/PRODUCT_SPEC.md) - 完整功能清单和产品规格
- [技术架构文档](docs/TECH_DOC.md) - 系统架构和技术选型详解
- [用户操作手册](docs/USER_MANUAL.md) - 面向最终用户的详细操作指南
- [API适配说明](docs/API_ADAPTATION_GUIDE.md) - 后端API文档，适合第三方集成
- [安装部署手册](docs/INSTALL.md) - 详细的安装部署步骤
- [功能分析报告](docs/PLATFORM_ANALYSIS.md) - 平台功能结构图和数据处理链路
- [产品手册](docs/COMPETITION_BROCHURE.md) - 产品亮点和市场价值
- [项目演示文稿](docs/PRESENTATION.md) - 项目介绍和核心亮点展示
- [工作流设计方案](docs/WORKFLOW_DESIGN.md) - 工作流重构设计文档

## 注意事项

1. 生产环境请修改 `backend/.env` 中的 `SECRET_KEY`
2. 生产环境建议切换至 MySQL 数据库
3. 上传文件大小限制可在配置中调整
4. AI功能需要配置 LLM API 密钥（在 AI配置页面设置）
5. Docker部署默认使用阿里云镜像加速，如需 Docker Hub 请修改配置

## 许可证

MIT License

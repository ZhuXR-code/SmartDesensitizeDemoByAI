# 敏感信息智能脱敏平台

## 项目概述

基于 Vue3 + FastAPI 的敏感信息识别与脱敏通用工具平台，支持多语言（中/英/日/韩/法/德）敏感数据识别和多种脱敏策略。

## 核心亮点

- **多语言智能识别**：支持6种语言的敏感数据识别，基于字符集特征自动检测语言
- **识别-脱敏一体化**：识别结果一键跳转脱敏，自动推荐最优脱敏规则
- **关联仿真脱敏**：基于密钥的确定性脱敏，保证跨表数据一致性
- **可视化前后对比**：脱敏前展示10-20条数据对比，确认后才执行全量处理
- **多种报告格式**：支持HTML在线预览和Markdown格式下载
- **前后端分离架构**：Vue3 + FastAPI，提供完整RESTful API，易于第三方集成
- **三种页面风格切换**：支持经典、暗紫、黑金三种主题风格，满足不同场景和个人喜好

## 技术架构

### 前端
- **框架**: Vue 3.4.15
- **UI 组件库**: Element Plus 2.5.3
- **状态管理**: Pinia 2.1.7
- **路由**: Vue Router 4.2.5
- **图表**: ECharts 5.4.3
- **HTTP 客户端**: Axios 1.6.7

### 后端
- **框架**: FastAPI 0.109.2
- **数据库**: SQLite (开发) / MySQL (生产)
- **ORM**: SQLAlchemy 2.0.27
- **数据处理**: Pandas 2.2.0

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+ (前端开发需要)

### 后端启动

```bash
cd backend

# 使用阿里镜像安装依赖
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 启动服务
python run.py
```

后端服务将运行在 http://localhost:8000

API 文档: http://localhost:8000/api/docs

### 前端启动

```bash
cd frontend

# 使用 npm 阿里镜像
npm config set registry https://registry.npmmirror.com

# 安装依赖
npm install

# 启动开发服务器
npm run serve
```

前端将运行在 http://localhost:8080

## 功能模块

### 1. 页面风格切换
- 支持三种主题风格：经典（默认）、暗紫、黑金
- 一键切换，实时生效
- 自动保存用户偏好到本地存储

### 2. 数据集管理
- 支持 Excel、CSV、TXT、JSON、Markdown、Log 等格式导入
- 支持剪贴板粘贴数据
- 支持数据库连接配置（MySQL/PostgreSQL/Oracle/SQL Server）
- 数据集预览和分页查看

### 3. 敏感数据识别
- 内置多语言识别规则（正则/关键词）
- 支持自定义识别规则
- 规则集管理（适应不同场景）
- 实时任务进度和日志
- 语言自动检测和分布统计

### 4. 数据脱敏
- 遮盖模式：部分遮盖、等长遮盖、固定长度遮盖
- 仿真替换：随机仿真、关联仿真（基于密钥）
- 30个内置密钥，支持安全隔离
- 脱敏效果预览确认
- 支持生成副本或覆盖原数据

### 5. 报表与结果
- 识别结果明细查看
- 脱敏前后对比
- 结果文件下载
- 历史任务管理
- **HTML报告在线预览**
- **Markdown报告下载**

## 项目结构

```
.
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置（日志、配置等）
│   │   ├── db/             # 数据库
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模型
│   │   └── services/       # 业务逻辑（识别引擎、脱敏引擎、报告生成器等）
│   ├── data/               # SQLite 数据文件
│   ├── uploads/            # 上传文件存储
│   ├── requirements.txt    # Python 依赖
│   └── run.py              # 启动脚本
│
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── api/            # API 封装
│   │   ├── components/     # 公共组件
│   │   ├── router/         # 路由配置
│   │   ├── views/          # 页面视图
│   │   └── App.vue         # 根组件
│   ├── package.json        # 依赖配置
│   └── vue.config.js       # Vue 配置
│
├── docs/                   # 项目文档
│   ├── USER_MANUAL.md      # 用户操作手册
│   ├── API_ADAPTATION_GUIDE.md  # API适配说明
│   └── PRESENTATION.md     # 项目演示文稿
│
├── test_data/              # 测试数据
└── README.md               # 项目说明
```

## 核心特性详解

### 多语言支持
支持中文、英语、日语、韩语、法语、德语的敏感数据识别和脱敏，基于字符集特征自动检测语言。

### 规则引擎
灵活的规则配置，支持正则和关键词匹配。内置丰富的识别规则，同时支持用户自定义规则。

### 关联脱敏
基于密钥的确定性脱敏算法，保证跨表数据一致性。不同密钥生成不同的脱敏结果，降低彩虹表攻击风险。

### 安全审计
完整的操作日志系统，记录所有API请求、数据库操作和安全事件，支持日志自动轮转和分级存储。

### 异步处理
大文件处理采用后台任务模式，支持实时进度查看，前端通过轮询获取任务状态。

## 开发说明

### 添加新的识别规则

在 `backend/app/services/detection_engine.py` 的 `BUILTIN_RULES` 列表中添加规则定义。

### 添加新的脱敏规则

在 `backend/app/services/desensitization_engine.py` 的 `BUILTIN_RULES` 列表中添加规则，并实现对应的处理方法。

### 数据库迁移

当前使用 SQLAlchemy 自动创建表结构。如需使用 Alembic 进行数据库迁移：

```bash
cd backend
alembic init migrations
```

## 注意事项

1. 生产环境请修改 `backend/.env` 中的 `SECRET_KEY`
2. 生产环境建议切换至 MySQL 数据库
3. 上传文件大小限制可在配置中调整
4. 定期清理临时文件以释放存储空间
5. PDF报告生成需要额外安装依赖（weasyprint/playwright/pdfkit），如未安装则自动降级为Markdown格式

## 相关文档

- [用户操作手册](docs/USER_MANUAL.md) - 面向最终用户的详细操作指南
- [API适配说明](docs/API_ADAPTATION_GUIDE.md) - 后端API文档，适合与其他系统集成
- [项目演示文稿](docs/PRESENTATION.md) - 项目介绍和核心亮点展示

## 许可证

MIT License

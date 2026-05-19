# 敏感信息脱敏平台 — 技术文档

> **版本：** v1.0  
> **技术栈：** Vue 3 + FastAPI + MySQL  
> **架构：** 前后端分离 (B/S)  

---

## 一、系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                     用户浏览器                                │
│           http://localhost:8080 / :5173                      │
└───────────────┬──────────────────────────────────────────────┘
                │  HTTP (REST API + Static Files)
┌───────────────▼──────────────────────────────────────────────┐
│                 Nginx / Dev Server                            │
│           前端静态文件 + API 反向代理                          │
└───────┬───────────────────────────┬──────────────────────────┘
        │  static files             │  /api/*
┌───────▼───────┐          ┌───────▼──────────────────────────┐
│   Frontend    │          │        Backend                    │
│   Vue 3 SPA   │          │     FastAPI (port 8000)           │
│   Element Plus│          │                                  │
│   ECharts     │          │  ┌────────────────────────────┐  │
│   Pinia       │          │  │   API Routes               │  │
│   Axios       │          │  │   /api/datasets            │  │
│   Vue Router  │          │  │   /api/detection           │  │
│   4 Themes    │          │  │   /api/desensitization     │  │
└───────────────┘          │  │   /api/ai                  │  │
                           │  │   /api/dashboard           │  │
                           │  │   /api/data-sources        │  │
                           │  │   /api/reports             │  │
                           │  │   /api/platform-report     │  │
                           │  └───────────┬────────────────┘  │
                           │  ┌───────────▼────────────────┐  │
                           │  │   Services Layer            │  │
                           │  │   detection_engine          │  │
                           │  │   desensitization_engine    │  │
                           │  │   ai_service                │  │
                           │  │   report_generator          │  │
                           │  │   language_detector         │  │
                           │  │   deterministic_masking     │  │
                           │  │   address_parser            │  │
                           │  │   db_connector              │  │
                           │  │   data_service              │  │
                           │  │   task_manager              │  │
                           │  └───────────┬────────────────┘  │
                           │  ┌───────────▼────────────────┐  │
                           │  │   SQLAlchemy ORM           │  │
                           │  └───────────┬────────────────┘  │
                           └──────────────┼───────────────────┘
                                          │
                                  ┌───────▼───────┐
                                  │  MySQL 8.0    │
                                  │  (port 3306)  │
                                  └───────────────┘
```

---

## 二、技术栈详解

### 2.1 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4 | 前端框架，Composition API |
| Vue Router | ^4.2 | SPA 路由 |
| Pinia | ^2.1 | 状态管理（替代 Vuex） |
| Element Plus | ^2.5 | UI 组件库 |
| ECharts | ^5.4 | 数据可视化图表 |
| Axios | ^1.6 | HTTP 请求 |
| Sass | ^1.70 | CSS 预处理 |

**前端工程化：** Vue CLI 5 + ESLint

### 2.2 四主题架构

```
src/
├── themes/
│   ├── classic/         # 经典风格（蓝白商务风）
│   │   ├── components/  # Layout.vue
│   │   ├── views/       # 所有页面的经典版
│   │   └── styles/      # 经典主题样式
│   ├── vue-classic/     # Vue经典风格（Element Plus 默认）
│   │   ├── components/  # Layout.vue
│   │   ├── views/       # 所有页面的Vue经典版
│   │   └── styles/      # Vue经典主题样式
│   ├── dark-purple/     # 暗紫风格（玻璃质感）
│   │   ├── components/  # Layout + GlassCard 等
│   │   ├── views/       # 所有页面的暗紫版
│   │   └── styles/      # wisteria-glass-theme.scss
│   └── black-gold/      # 黑金风格（素雅大地色）
│       ├── components/  # Layout
│       ├── views/       # 所有页面的黑金版
│       └── styles/      # 黑金主题样式
├── components/
│   ├── ThemeLoader.vue  # 动态加载主题组件
│   └── ThemeLayout.vue  # 动态加载主题 Layout
├── stores/
│   └── theme.js         # 主题切换状态
└── styles/
    ├── theme-dark-purple.scss
    ├── theme-black-gold.scss
    └── theme-classic.scss
```

**实现原理：** 路由所有页面使用 `ThemeLoader` 组件，该组件根据当前主题 `dynamic import()` 对应主题目录下的 .vue 文件。Layout 同理由 `ThemeLayout` 动态加载。

### 2.3 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.109 | 异步 Web 框架 |
| Uvicorn | 0.27 | ASGI 服务器 |
| SQLAlchemy | 2.0 | ORM |
| PyMySQL | 1.1 | MySQL 驱动 |
| Pandas | 2.2 | 数据处理 |
| langdetect | 1.0 | 语言检测 |
| openpyxl | 3.1 | Excel 读写 |
| python-jose | 3.3 | JWT 认证 |
| httpx | 0.26 | LLM API HTTP 客户端 |

### 2.4 后端模块

```
backend/app/
├── api/                    # API 路由层
│   ├── dataset.py          # 数据集 CRUD + 上传
│   ├── detection.py        # 规则引擎识别任务 + 规则管理
│   ├── desensitization.py  # 规则引擎脱敏任务 + 规则 + 密钥 + 报告
│   ├── ai.py               # AI智能模块（配置/识别/脱敏/复核/报告）
│   ├── dashboard.py        # 首页统计
│   ├── datasource.py       # 数据源管理
│   ├── report.py           # 报告接口
│   └── platform_report.py  # 运营报表（领导视图）
├── services/               # 业务逻辑层
│   ├── detection_engine.py           # 规则引擎识别
│   ├── desensitization_engine.py     # 规则引擎脱敏
│   ├── ai_service.py                 # AI大模型调用（LLM识别/脱敏）
│   ├── task_manager.py               # 异步任务取消管理
│   ├── report_generator.py           # 报告生成（HTML/MD）
│   ├── language_detector.py          # 多语言检测
│   ├── deterministic_masking.py      # 关联造数算法
│   ├── address_parser.py             # 地址解析
│   ├── db_connector.py               # 数据库连接
│   └── data_service.py               # 数据服务
├── models/                 # 数据模型
│   ├── detection.py        # 规则引擎识别模型
│   ├── desensitization.py  # 规则引擎脱敏模型
│   ├── ai.py               # AI智能模块模型
│   ├── dataset.py          # 数据集模型
│   ├── report.py           # 报表模型
│   └── user.py             # 用户模型
├── schemas/                # Pydantic 校验
│   ├── detection.py
│   ├── desensitization.py
│   ├── ai.py
│   ├── dataset.py
│   └── common.py
├── core/
│   ├── config.py           # 配置（.env）
│   └── logger.py           # 日志
└── db/
    └── database.py         # 数据库连接池
```

---

## 三、关键算法

### 3.1 多语言自动检测

基于字符集 Unicode 码范围分析：
- CJK 字符（0x4E00-0x9FFF）→ 中文/日文
- 假名字符（0x3040-0x30FF）→ 日文
- 谚文字符（0xAC00-0xD7AF）→ 韩文
- 拉丁扩展 → 英文/法文/德文
- 辅助 langdetect 库做二级判断

检测流程：
```
每行数据 → Unicode 码位分析 → 候选语言
         → langdetect 校验 → 确定语言 → 调用对应规则
```

### 3.2 关联仿真（确定性脱敏）

核心流程：
```
原始值 + 密钥 → HMAC-SHA256 → 随机种子 → 查仿真字典 → 假数据
```

- 相同输入 + 相同密钥 = 相同假数据（跨表一致）
- 不同密钥 = 完全不同的假数据（业务隔离）
- 30组独立密钥保证安全

### 3.3 规则引擎敏感识别

采用 **正则表达式 + 关键词 + 格式校验** 三层匹配：
```
列数据 → 正则预筛选 → 格式校验（如身份证校验码）
      → 关键词匹配 → 置信度评分 → 结果输出
```

### 3.4 AI大模型敏感识别

采用 **LLM语义分析** 替代传统正则匹配，通过构造提示词实现：
```
数据集 → 逐行逐列 → 构造AI提示词（字段名+值+法规背景）
       → 调用LLM API → 解析JSON响应
       → { is_sensitive, sensitive_type, confidence, risk_level, regulation_ref }
       → 人工复核 → 复核结果驱动脱敏
```

**支持的大模型：** OpenAI / DeepSeek / 千问(Qwen) / Kimi / GLM / 文心 / Azure / 自定义

---

## 四、API 接口完整列表

### 4.1 数据集

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/datasets/list | 数据集列表 |
| POST | /api/datasets/upload | 文件上传 |
| POST | /api/datasets/from-text | 剪贴板文本创建数据集 |
| GET | /api/datasets/{id} | 数据集详情 |
| GET | /api/datasets/{id}/preview | 数据集预览 |
| DELETE | /api/datasets/{id} | 删除数据集 |

### 4.2 数据源

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/data-sources/test-connection | 测试数据库连接 |
| POST | /api/data-sources/tables | 获取表列表 |
| POST | /api/data-sources/table-preview | 预览表数据 |
| POST | /api/data-sources/save-and-import | 保存并导入 |
| GET | /api/data-sources/list | 数据源列表 |
| GET | /api/data-sources/{id}/datasets | 关联数据集 |
| DELETE | /api/data-sources/{id} | 删除数据源 |

### 4.3 识别任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/detection/tasks | 任务列表 |
| POST | /api/detection/tasks | 创建任务 |
| GET | /api/detection/tasks/{id} | 任务详情 |
| POST | /api/detection/tasks/{id}/cancel | 取消任务 |
| POST | /api/detection/tasks/{id}/jump-to-desensitization | 跳转脱敏 |
| GET | /api/detection/rules | 规则列表 |
| POST | /api/detection/rules | 创建规则 |
| GET | /api/detection/rule-sets | 规则集列表 |
| POST | /api/detection/rule-sets | 创建规则集 |

### 4.4 脱敏任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/desensitization/tasks | 任务列表 |
| POST | /api/desensitization/tasks | 创建任务 |
| GET | /api/desensitization/tasks/{id} | 任务详情 |
| POST | /api/desensitization/tasks/{id}/cancel | 取消任务 |
| GET | /api/desensitization/rules | 脱敏规则 |
| GET | /api/desensitization/keys | 脱敏密钥 |
| POST | /api/desensitization/preview | 预览脱敏效果 |
| GET | /api/desensitization/tasks/{id}/download | 下载副本 |
| POST | /api/desensitization/tasks/{id}/generate-report | 生成报告 |
| GET | /api/desensitization/tasks/{id}/download-report | 下载报告 |

### 4.5 AI智能模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/ai/configs | 所有AI配置 |
| GET | /api/ai/config | 当前激活配置 |
| POST | /api/ai/config | 保存配置 |
| PUT | /api/ai/config/{id} | 更新配置 |
| DELETE | /api/ai/config/{id} | 删除配置 |
| POST | /api/ai/config/{id}/activate | 激活配置 |
| POST | /api/ai/config/test | 测试连接 |
| POST | /api/ai/detection/tasks | 创建AI识别任务 |
| GET | /api/ai/detection/tasks | AI识别任务列表 |
| GET | /api/ai/detection/tasks/{id} | AI识别详情 |
| POST | /api/ai/detection/tasks/{id}/cancel | 取消AI识别 |
| GET | /api/ai/detection/tasks/{id}/review | 待复核列表 |
| POST | /api/ai/detection/tasks/{id}/review | 提交复核 |
| POST | /api/ai/desensitization/tasks | 创建AI脱敏任务 |
| GET | /api/ai/desensitization/tasks | AI脱敏任务列表 |
| GET | /api/ai/desensitization/tasks/{id} | AI脱敏详情 |
| POST | /api/ai/desensitization/tasks/{id}/cancel | 取消AI脱敏 |
| GET | /api/ai/desensitization/tasks/{id}/download | 下载AI脱敏文件 |
| POST | /api/ai/desensitization/tasks/{id}/generate-report | 生成AI报告 |
| GET | /api/ai/desensitization/tasks/{id}/download-report | 下载AI报告 |

### 4.6 运营报表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/platform-report/overview | 核心KPI |
| GET | /api/platform-report/security-value | 安全价值 |
| GET | /api/platform-report/efficiency | 效率统计 |
| GET | /api/platform-report/technology | 技术亮点 |
| GET | /api/platform-report/compliance | 合规成果 |

---

## 五、数据库表关系

```
datasets ──1:N── detection_tasks ──1:N── detection_results
   │                    │
   │                    └── 引用 detection_rule_sets
   │
   ├───1:N── desensitization_tasks ──1:N── desensitization_results
   │                    │
   │                    ├── 引用 detection_tasks
   │                    ├── 引用 desensitization_keys
   │                    └── 引用 desensitization_rules
   │
   ├───1:N── ai_detection_tasks ──1:N── ai_detection_results
   │                    │
   │                    └── 引用 ai_configs
   │
   └───1:N── ai_desensitization_tasks ──1:N── ai_desensitization_results
                        │
                        └── 引用 ai_configs

data_sources ──1:N── datasets
ai_configs (独立配置表)
desensitization_keys (独立密钥表)
```

---

## 六、部署架构

### 开发环境
- 前端：`npm run serve` (port 8080)
- 后端：`python run.py` (port 8000)
- 数据库：SQLite / MySQL 8.0

### 生产环境（三种方案）

| 方案 | 前端 | 后端 | 数据库 | 启动方式 |
|------|------|------|--------|---------|
| Docker 部署 | Nginx 静态文件 | Uvicorn | MySQL 8.0 | `一键部署.bat` |
| 便携式部署 | Vue CLI Server | Uvicorn | SQLite | `启动平台.bat` |
| 手动部署 | Nginx 静态文件 | Gunicorn+Uvicorn | MySQL 8.0 | 手动配置 |

### Docker 架构
```
Nginx (port 8080)
  ├── / → 前端静态文件
  └── /api/ → 反向代理 backend:8000

Backend (port 8000)
  └── MySQL (port 3306)
```

---

## 七、性能指标

| 指标 | 值 | 说明 |
|------|---|------|
| API 响应时间 | <200ms (P95) | 常规查询 |
| 文件上传 | 100MB / ~30s | 取决于带宽 |
| 规则引擎识别吞吐 | ~2000 行/秒 | 6语言全开 |
| 规则引擎脱敏吞吐 | ~1500 行/秒 | 含仿真算法 |
| AI识别 | 取决于LLM API响应速度 | 通常 2-5秒/行 |
| AI脱敏 | 取决于LLM API响应速度 | 通常 1-3秒/行 |
| 报告生成 | <10s (万行) | HTML/MD |
| 首屏加载 | <2s | gzip 压缩 |

---

## 八、项目里程碑

| 阶段 | 内容 | 状态 |
|------|------|------|
| V1.0 | 核心功能（文件上传、多语言识别、脱敏、报告） | ✅ 完成 |
| V1.0 | AI智能模块（LLM识别、AI脱敏、人工复核） | ✅ 完成 |
| V1.0 | 四套UI主题（经典/Vue经典/暗紫/黑金） | ✅ 完成 |
| V1.0 | 平台运营成效报表 | ✅ 完成 |
| V1.0 | 快速脱敏工作流（引导式4步流程） | ✅ 完成 |
| V1.0 | 三种部署方案（Docker/便携式/Windows安装包） | ✅ 完成 |
| V1.1 | 用户帮助文档 | ✅ 完成 |
| V1.1 | CLI命令行工具 | ✅ 完成 |

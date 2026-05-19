# 敏感信息脱敏平台 — 技术文档

> **版本：** v1.0  
> **技术栈：** Vue 3 + FastAPI + MySQL  
> **架构：** 前后端分离 (B/S)  

---

## 一、系统架构

```
┌──────────────────────────────────────────────────────┐
│                     用户浏览器                         │
│           http://localhost:8080                       │
└───────────────┬──────────────────────────────────────┘
                │  HTTP (REST API + Static Files)
┌───────────────▼──────────────────────────────────────┐
│                 Nginx / Dev Server                    │
│           前端静态文件 + API 反向代理                    │
└───────┬───────────────────────────┬──────────────────┘
        │  static files             │  /api/*
┌───────▼───────┐          ┌───────▼──────────────────┐
│   Frontend    │          │        Backend             │
│   Vue 3 SPA   │          │     FastAPI (port 8000)     │
│   Element Plus│          │                             │
│   ECharts     │          │  ┌───────────────────────┐ │
│   Pinia       │          │  │   API Routes          │ │
│   Axios       │          │  │   /api/datasets       │ │
│   Vue Router  │          │  │   /api/detection      │ │
│   4 Themes    │          │  │   /api/desensitization│ │
└───────────────┘          │  │   /api/platform-report│ │
                           │  └───────────┬───────────┘ │
                           │  ┌───────────▼───────────┐ │
                           │  │   Services Layer      │ │
                           │  │   detection_engine     │ │
                           │  │   desensitization_engine│ │
                           │  │   report_generator     │ │
                           │  │   language_detector    │ │
                           │  │   deterministic_masking│ │
                           │  │   address_parser       │ │
                           │  │   db_connector         │ │
                           │  │   ai_service           │ │
                           │  │   task_manager         │ │
                           │  └───────────┬───────────┘ │
                           │  ┌───────────▼───────────┐ │
                           │  │   SQLAlchemy ORM      │ │
                           │  └───────────┬───────────┘ │
                           └──────────────┼─────────────┘
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

### 2.2 三主题架构（独创）

```
src/
├── themes/
│   ├── classic/         # 经典风格（蓝白）
│   │   ├── components/  # Layout.vue
│   │   ├── views/       # 所有页面的经典版
│   │   └── styles/      # 经典主题样式
│   ├── dark-purple/     # 暗紫风格
│   │   ├── components/  # Layout + GlassCard 等
│   │   ├── views/       # 所有页面的暗紫版
│   │   └── styles/      # wisteria-glass-theme.scss
│   └── black-gold/      # 黑金风格
│       ├── components/  # Layout
│       ├── views/       # 所有页面的黑金版
│       └── styles/      # 素雅大地色系
├── components/
│   ├── ThemeLoader.vue  # 动态加载主题组件
│   └── ThemeLayout.vue  # 动态加载主题 Layout
├── stores/
│   └── theme.js         # 主题切换状态
└── styles/
    ├── theme-dark-purple.scss
    └── theme-black-gold.scss
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

### 2.4 后端模块

```
backend/app/
├── api/                    # API 路由层
│   ├── dataset.py          # 数据集 CRUD + 上传
│   ├── detection.py        # 识别任务 + 规则管理
│   ├── desensitization.py  # 脱敏任务 + 规则 + 密钥 + 报告
│   ├── dashboard.py        # 首页统计
│   ├── datasource.py       # 数据源管理
│   ├── report.py           # 报告接口
│   └── platform_report.py  # 运营报表
├── services/               # 业务逻辑层
│   ├── detection_engine.py          # 识别引擎
│   ├── desensitization_engine.py    # 脱敏引擎
│   ├── report_generator.py         # 报告生成（HTML/MD）
│   ├── language_detector.py        # 多语言检测
│   ├── deterministic_masking.py    # 关联造数算法
│   ├── address_parser.py           # 地址解析
│   ├── db_connector.py             # 数据库连接
│   └── data_service.py             # 数据服务
├── models/                 # 数据模型
│   ├── detection.py
│   ├── desensitization.py
│   ├── dataset.py
│   ℞── report.py
│   └── user.py
├── schemas/                # Pydantic 校验
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

### 3.3 敏感信息识别

采用 **正则表达式 + 关键词 + 格式校验** 三层匹配：
```
列数据 → 正则预筛选 → 格式校验（如身份证校验码）
      → 关键词匹配 → 置信度评分 → 结果输出
```

---

## 四、API 接口

### 4.1 数据集

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/datasets/list | 数据集列表 |
| POST | /api/datasets/upload | 文件上传 |
| GET | /api/datasets/{id} | 数据集详情 |
| DELETE | /api/datasets/{id} | 删除数据集 |

### 4.2 识别任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/detection/tasks | 任务列表 |
| POST | /api/detection/tasks | 创建任务 |
| GET | /api/detection/tasks/{id} | 任务详情 |
| POST | /api/detection/jump-to-desensitization/{id} | 跳转脱敏 |

### 4.3 脱敏任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/desensitization/tasks | 任务列表 |
| POST | /api/desensitization/tasks | 创建任务 |
| GET | /api/desensitization/tasks/{id} | 任务详情 |
| GET | /api/desensitization/rules | 脱敏规则 |
| GET | /api/desensitization/keys | 脱敏密钥 |
| POST | /api/desensitization/generate-report/{id} | 生成报告 |
| GET | /api/desensitization/download-report/{id} | 下载报告 |
| GET | /api/desensitization/download-file/{id} | 下载副本 |

### 4.4 运营报表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/platform-report/overview | 总览 |
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
   └────1:N── desensitization_tasks ──1:N── desensitization_results
                    │
                    ├── 引用 detection_tasks
                    ├── 引用 desensitization_keys
                    └── 引用 desensitization_rules
```

---

## 六、部署架构

### 开发环境
- 前端：`npm run serve` (port 8080)
- 后端：`python run.py` (port 8000)
- 数据库：MySQL 8.0 (port 3306)

### 生产环境
- 前端：Nginx 静态文件服务
- 后端：Gunicorn + Uvicorn workers
- 数据库：MySQL 8.0 / MariaDB
- 可选：Docker Compose 一键部署

---

## 七、性能指标

| 指标 | 值 | 说明 |
|------|---|------|
| API 响应时间 | <200ms (P95) | 常规查询 |
| 文件上传 | 100MB / ~30s | 取决于带宽 |
| 识别吞吐 | ~2000 行/秒 | 6语言全开 |
| 脱敏吞吐 | ~1500 行/秒 | 含仿真算法 |
| 报告生成 | <10s (万行) | HTML/MD |
| 首屏加载 | <2s | gzip 压缩 |

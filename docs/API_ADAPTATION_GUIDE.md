# 后端 API 适配说明文档

## 概述

本项目后端采用 **FastAPI** 框架开发，提供完整的 RESTful API 接口。FastAPI 自动生成 OpenAPI 文档（Swagger UI），非常适合与其他前端框架或 AI 工具进行适配。

## 技术栈

- **框架**: FastAPI 0.109.2
- **数据库**: SQLite (开发) / MySQL (生产)
- **ORM**: SQLAlchemy 2.0.27
- **异步**: 原生支持 async/await
- **API 文档**: 自动生成 Swagger UI (/api/docs) 和 ReDoc (/api/redoc)

## API 文档访问

启动后端服务后，可通过以下地址访问自动生成的 API 文档：

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 通用响应格式

所有 API 返回统一的响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

## 核心 API 模块

### 1. 首页仪表盘

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/dashboard/stats | 获取仪表盘统计数据 |

### 2. 数据集管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/datasets/upload | 上传文件导入数据集 |
| POST | /api/datasets/from-text | 从剪贴板文本创建数据集 |
| GET | /api/datasets/list | 获取数据集列表 |
| GET | /api/datasets/{id} | 获取数据集详情 |
| GET | /api/datasets/{id}/preview | 预览数据集内容 |
| DELETE | /api/datasets/{id} | 删除数据集 |

### 3. 数据源管理（数据库连接）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/data-sources/test-connection | 测试数据库连接 |
| POST | /api/data-sources/tables | 获取数据库表列表 |
| POST | /api/data-sources/table-preview | 预览指定表的数据 |
| POST | /api/data-sources/save-and-import | 保存数据源并导入选中表到数据集 |
| GET | /api/data-sources/list | 获取已配置的数据源列表 |
| GET | /api/data-sources/{id}/datasets | 获取数据源关联的数据集 |
| DELETE | /api/data-sources/{id} | 删除数据源（同时删除关联数据集） |

**数据库连接测试示例：**
```bash
curl -X POST "http://localhost:8000/api/data-sources/test-connection" \
  -H "Content-Type: application/json" \
  -d '{
    "db_type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "username": "root",
    "password": "password"
  }'
```

**导入选中表到数据集示例：**
```bash
curl -X POST "http://localhost:8000/api/data-sources/save-and-import" \
  -H "Content-Type: application/json" \
  -d '{
    "source_name": "生产环境MySQL",
    "db_type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "username": "root",
    "password": "password",
    "selected_tables": ["users", "orders", "products"],
    "name_prefix": "生产_"
  }'
```
响应会返回每个表对应创建的数据集ID，可直接用于后续的识别/脱敏任务。

### 4. 敏感数据识别

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/detection/rules | 获取识别规则列表 |
| POST | /api/detection/rules | 创建自定义识别规则 |
| DELETE | /api/detection/rules/{id} | 删除识别规则 |
| GET | /api/detection/rule-sets | 获取规则集列表 |
| POST | /api/detection/rule-sets | 创建规则集 |
| DELETE | /api/detection/rule-sets/{id} | 删除规则集 |
| POST | /api/detection/tasks | 创建识别任务 |
| GET | /api/detection/tasks | 获取识别任务列表 |
| GET | /api/detection/tasks/{id} | 获取任务详情 |
| GET | /api/detection/tasks/{id}/results | 获取识别结果 |
| POST | /api/detection/tasks/{id}/jump-to-desensitization | 一键跳转脱敏 |

### 5. 数据脱敏

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/desensitization/rules | 获取脱敏规则列表 |
| POST | /api/desensitization/rules | 创建自定义脱敏规则 |
| GET | /api/desensitization/keys | 获取脱敏密钥列表 |
| POST | /api/desensitization/preview | 预览脱敏效果 |
| POST | /api/desensitization/tasks | 创建脱敏任务 |
| GET | /api/desensitization/tasks | 获取脱敏任务列表 |
| GET | /api/desensitization/tasks/{id} | 获取脱敏任务详情 |
| GET | /api/desensitization/tasks/{id}/results | 获取脱敏结果 |
| GET | /api/desensitization/tasks/{id}/download | 下载脱敏后的文件 |

### 6. 报告管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/desensitization/tasks/{id}/generate-report | 生成脱敏报告 |
| GET | /api/desensitization/tasks/{id}/download-report | 下载报告（支持HTML/Markdown格式） |

**下载报告示例：**
```bash
# 下载HTML格式报告
curl -X GET "http://localhost:8000/api/desensitization/tasks/1/download-report?format=html" \
  -o report.html

# 下载Markdown格式报告
curl -X GET "http://localhost:8000/api/desensitization/tasks/1/download-report?format=markdown" \
  -o report.md
```

**报告格式说明：**
- **HTML格式**: 适合在线预览，包含完整的样式和图表
- **Markdown格式**: 适合存档和版本管理，纯文本格式

## 适配其他前端/AI 的注意事项

### 1. CORS 配置

后端已配置允许所有跨域请求：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 文件上传

文件上传使用 multipart/form-data 格式：

```bash
curl -X POST "http://localhost:8000/api/datasets/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data.csv" \
  -F "name=测试数据集"
```

### 3. 异步任务状态轮询

识别和脱敏任务采用后台异步执行模式：

1. 创建任务后返回任务 ID 和初始状态 `pending`
2. 客户端通过轮询 `GET /api/detection/tasks/{id}` 获取最新状态
3. 状态变化：`pending` -> `running` -> `completed`/`failed`

### 4. 数据库切换

默认使用 SQLite，生产环境可切换至 MySQL：

修改 `backend/.env` 文件：
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/desensitization
```

### 5. 扩展开发

如需新增 API 端点，在 `backend/app/api/` 目录下创建新的路由文件，然后在 `backend/app/main.py` 中注册：

```python
from app.api import new_module
app.include_router(new_module.router)
```

## 环境要求

- Python 3.8+
- 依赖安装：`pip install -r requirements.txt`
- 启动服务：`python run.py`

## 数据库模型

详见 `backend/app/models/` 目录下的模型定义，主要包含：

- `User` / `Role`: 用户和角色
- `Dataset` / `DataSource`: 数据集和数据源
- `DetectionRule` / `DetectionRuleSet` / `DetectionTask` / `DetectionResult`: 识别相关
- `DesensitizationRule` / `DesensitizationKey` / `DesensitizationTask` / `DesensitizationResult`: 脱敏相关
- `Report`: 报表

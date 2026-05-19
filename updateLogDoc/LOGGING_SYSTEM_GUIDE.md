# 日志系统使用指南

## 概述

本文档介绍平台日志系统的配置、使用方法和故障排查技巧。

## 日志系统架构

### 后端日志系统

**位置**: `backend/app/core/logger.py`

**功能特性**:
- 多级别日志输出（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 多文件分离存储
- 自动轮转（按大小/时间）
- 控制台 + 文件双输出
- 详细的上下文信息（时间、模块、函数、行号）

**日志文件说明**:

| 日志文件 | 用途 | 保留策略 |
|---------|------|---------|
| `app_YYYY-MM-DD.log` | 主日志（所有操作） | 50MB x 30个备份 |
| `error_YYYY-MM-DD.log` | 错误日志（仅ERROR以上） | 20MB x 10个备份 |
| `api_YYYY-MM-DD.log` | API访问日志 | 50MB x 15个备份 |
| `database_YYYY-MM-DD.log` | 数据库操作日志 | 30MB x 10个备份 |
| `security_YYYY-MM-DD.log` | 安全审计日志 | 20MB x 30个备份 |

**日志格式示例**:
```
2026-05-16 15:30:45 | INFO     | app.api.datasource            | test_connection        | L45    | 测试数据库连接 | 类型: mysql | 主机: localhost:3308
2026-05-16 15:30:46 | DEBUG    | app.services.db_connector     | test_connection        | L52    | 正在执行测试查询...
2026-05-16 15:30:46 | INFO     | app.services.db_connector     | test_connection        | L58    | 数据库连接成功 | 耗时: 123.45ms
```

### API请求日志中间件

**位置**: `backend/app/main.py`

**记录内容**:
- 所有HTTP请求（方法、路径、客户端IP）
- 请求参数（自动脱敏密码等敏感信息）
- 响应状态码和耗时
- 未捕获异常的完整堆栈跟踪
- 响应头添加 `X-Process-Time` 耗时信息

### 前端请求日志拦截器

**位置**: `frontend/src/api/request.js`

**增强的错误处理**:
- 请求开始时间和URL记录
- 请求数据记录（自动脱敏敏感字段）
- 响应状态码和耗时统计
- HTTP错误分类（400/401/403/404/500/502/503/504）
- 404错误特别标记（显示完整路径便于调试）
- 500错误详细响应数据记录
- 网络超时检测

## 日志查看方法

### 实时日志

**后端终端**: 启动服务后会直接在控制台看到所有INFO及以上级别的日志。

**浏览器控制台**: 前端所有API请求和响应都会在Console中显示。

### 历史日志文件

```bash
# 进入日志目录
cd backend/logs

# 查看今天的所有日志
type app_2026-05-16.log

# 只看错误
type error_2026-05-16.log

# 查看API访问日志
type api_2026-05-16.log

# 查看数据库操作
type database_2026-05-16.log

# 查看安全事件
type security_2026-05-16.log
```

### 日志搜索技巧

```bash
# Windows PowerShell
Get-Content app_*.log | Select-String "测试数据库连接"

# 或使用 findstr
findstr "测试数据库连接" app_*.log

# 查找所有ERROR级别的日志
findstr "ERROR" error_*.log

# 查找特定异常
findstr "Exception" error_*.log
```

## 常见问题排查

### 数据库连接失败

**日志位置**:
- `backend/logs/error_YYYY-MM-DD.log` - 异常堆栈
- `backend/logs/api_YYYY-MM-DD.log` - API调用记录
- `backend/logs/database_YYYY-MM-DD.log` - 连接尝试记录

**关键日志关键词**:
- `测试数据库连接`
- `数据库连接失败`
- `Access denied` (MySQL认证失败)
- `Connection refused` (服务未启动)
- `Unknown database` (数据库不存在)

### 表导入失败

**日志追踪路径**:
1. 前端Console → `POST /api/data-sources/save-and-import` 失败
2. 后端主日志 → `保存数据源并导入表` 开始
3. 数据库日志 → 每个表的导入进度
4. 错误日志 → 具体异常堆栈

### 性能问题排查

```bash
# 在 database_*.log 中查找耗时较长的操作
findstr "耗时:" database_*.log
```

**优化建议**:
- 单次读取超过10000行的表考虑分页
- 查询耗时超过3秒的需要优化索引或SQL

## 日志配置调整

### 修改日志级别

编辑 `backend/.env`:
```env
# 开发环境建议 DEBUG，生产环境建议 INFO 或 WARNING
LOG_LEVEL=DEBUG
```

### 修改日志目录

```env
LOG_DIR=./logs
# 可以改为绝对路径
# LOG_DIR=D:/logs/desensitization
```

### 调整日志轮转策略

编辑 `backend/app/core/logger.py`:
```python
# 主日志：每个文件最大50MB，保留30个备份
file_handler = RotatingFileHandler(
    main_log_file,
    maxBytes=50*1024*1024,  # 50MB
    backupCount=30           # 保留30个旧文件
)
```

## 安全注意事项

### 敏感信息保护

**已实现的自动脱敏**:
- 密码字段自动替换为 `***`
- Token字段自动隐藏
- 数据库密码不在日志中明文显示

**禁止在日志中记录的信息**:
- 用户明文密码
- API密钥
- 数据库完整连接字符串中的密码
- 身份证号、银行卡号等PII数据

### 日志文件权限

**生产环境建议**:
- 设置日志目录权限（仅管理员可写）
- 定期归档和清理旧日志
- 敏感日志单独存储并加密

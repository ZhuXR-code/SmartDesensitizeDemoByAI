# 数据库导入功能测试指南

## 概述

本文档介绍如何测试和验证数据库导入功能，包括环境配置、测试步骤和故障排查。

## 环境配置

### 数据库配置

**配置文件**: `backend/.env`

```env
# MySQL配置示例
DATABASE_URL=mysql+pymysql://root:msps@localhost:3308/desensitization?charset=utf8mb4
```

**支持的数据库**:
- MySQL (默认端口3306)
- PostgreSQL (默认端口5432)
- Oracle (默认端口1521)
- SQL Server (默认端口1433)

### 测试数据库准备

**数据库名**: `desensitization`
**字符集**: `utf8mb4` (支持中文)

#### 测试表结构

##### 1. employees（员工表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| name | VARCHAR(100) | 姓名 |
| email | VARCHAR(100) | 邮箱 |
| phone | VARCHAR(20) | 电话 |
| department | VARCHAR(50) | 部门 |
| salary | DECIMAL(10,2) | 薪资 |
| hire_date | DATE | 入职日期 |
| address | TEXT | 地址 |

##### 2. customers（客户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| customer_name | VARCHAR(100) | 客户名称 |
| contact_phone | VARCHAR(20) | 联系电话 |
| email | VARCHAR(100) | 邮箱 |
| company | VARCHAR(100) | 公司 |
| address | TEXT | 地址 |
| credit_level | VARCHAR(20) | 信用等级 |
| create_time | DATETIME | 创建时间 |

##### 3. products（产品表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| product_name | VARCHAR(200) | 产品名称 |
| category | VARCHAR(50) | 分类 |
| price | DECIMAL(10,2) | 价格 |
| stock_quantity | INT | 库存数量 |
| description | TEXT | 描述 |
| supplier | VARCHAR(100) | 供应商 |

## 测试步骤

### 1. 启动服务

```bash
# 启动后端服务
cd backend
python -m uvicorn app.main:app --reload --port 8000

# 启动前端服务
cd frontend
npm run serve
```

### 2. 配置数据源

1. 访问平台: http://localhost:8080
2. 进入 **"数据集管理"** → **"导入数据"**
3. 选择 **"从数据库导入"** 标签页
4. 点击 **"去配置新数据源"**

**配置信息示例**:
```
数据源名称：本地MySQL测试库
数据库类型：MySQL
主机地址：localhost
端口：3308
用户名：root
密码：msps
数据库名：desensitization
```

5. 点击 **"测试连接"** 验证连接
6. 保存数据源配置

### 3. 导入数据

1. 在导入页面选择刚创建的数据源
2. 从下拉列表中选择表：
   - employees（员工信息）
   - customers（客户信息）
   - products（产品信息）
3. 查看表预览数据
4. 输入数据集名称
5. 点击 **"导入为数据集"**

### 4. 验证导入结果

1. 导入成功后跳转到数据集列表
2. 查看导入的数据集详情
3. 验证数据完整性

## 测试数据特点

### 包含敏感信息类型

- **个人隐私**: 姓名、手机号、邮箱、地址
- **企业信息**: 公司名称、联系方式、地址
- **财务信息**: 薪资数据
- **联系信息**: 电话、邮箱

### 数据真实性

- 使用真实的中国公司名称
- 使用真实的手机号格式
- 使用真实的地址格式
- 涵盖多个城市（北京、上海、广州、深圳、杭州）

## 故障排查

### 连接失败

1. **检查MySQL服务是否运行**
```bash
netstat -an | findstr 3308
```

2. **验证数据库是否存在**
```bash
mysql -u root -pmsps -P 3308 -e "SHOW DATABASES;"
```

3. **检查表是否创建成功**
```bash
mysql -u root -pmsps -P 3308 desensitization -e "SHOW TABLES;"
```

4. **查看后端日志**
- 后端控制台会显示详细的错误信息
- 检查数据库连接字符串是否正确

### 404错误

1. **确认前端已重新编译**
- 修改API文件后需要重启前端开发服务器
- 清除浏览器缓存（Ctrl+F5强制刷新）

2. **检查代理配置**
- 确认 `vue.config.js` 中的代理配置正确
- 确保后端在8000端口运行

3. **查看浏览器开发者工具**
- F12打开开发者工具
- Network 标签页查看请求URL和响应状态

## 下一步测试

完成基础导入功能测试后，可以继续测试：

1. **敏感数据识别**
   - 对导入的数据集创建识别任务
   - 验证能否识别出姓名、手机号、邮箱等敏感字段

2. **数据脱敏**
   - 对识别出的敏感数据进行脱敏处理
   - 测试不同的脱敏规则（掩码、替换、删除等）

3. **批量操作**
   - 同时导入多个表
   - 批量执行识别和脱敏任务

4. **报告生成**
   - 生成脱敏效果报告
   - 验证报告中的统计数据
   - 测试HTML在线预览和Markdown下载

## 技术细节

### 数据库连接配置

```
Connection String: mysql+pymysql://root:msps@localhost:3308/desensitization?charset=utf8mb4
Driver: PyMySQL
ORM: SQLAlchemy
Pool: SQLAlchemy connection pool with pre_ping
```

### API路由映射

```
前端请求路径: /api/data-sources/*
代理转发到: http://localhost:8000/api/data-sources/*
后端路由处理: app.api.datasource.router
```

### 文件存储位置

```
上传目录: ./uploads
导入的CSV文件: ./uploads/db_{source_id}_{table_name}_{timestamp}.csv
数据库记录: desensitization SQLite/MySQL
```

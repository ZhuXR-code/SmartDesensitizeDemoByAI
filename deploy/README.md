# 敏感信息脱敏平台 — Docker 快速部署指南

## 前置要求

- [Docker](https://www.docker.com/get-started) 已安装
- [Docker Compose](https://docs.docker.com/compose/install/) 已安装

## 一键部署（3步）

### 第1步：进入部署目录

```bash
cd deploy
```

### 第2步：启动所有服务

```bash
docker-compose up -d
```

首次启动会自动：
1. 拉取 MySQL 8.0 镜像
2. 创建 `desensitization2` 数据库
3. 执行 `init_db.sql` 创建19张表
4. 导入52条内置脱敏规则 + 30组脱敏密钥 + 规则集
5. 构建后端镜像并启动 (port 8000)
6. 构建前端镜像并启动 (port 8080)

### 第3步：访问平台

浏览器打开：**http://localhost:8080**

API 文档：**http://localhost:8000/api/docs**

---

## 服务端口

| 服务 | 端口 |
|------|------|
| 前端页面 | 8080 |
| 后端 API | 8000 |
| MySQL 数据库 | 3308 |

---

## 常用命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 只查看某个服务的日志
docker-compose logs -f backend

# 重启所有服务
docker-compose restart

# 停止所有服务
docker-compose down

# 停止并删除数据卷（⚠️ 会丢失数据）
docker-compose down -v

# 重新构建
docker-compose up -d --build
```

---

## 数据库信息

| 项目 | 值 |
|------|---|
| 地址 | localhost:3308 |
| 数据库名 | desensitization2 |
| 用户名 | root |
| 密码 | msps |

**内置数据：**
- 脱敏规则 52 条（遮盖/仿真/关联造数，6语言全覆盖）
- 脱敏密钥 30 组（用于业务隔离）
- 规则集 2 个（通用 + 专用场景）

---

## 非 Docker 部署

如果不使用 Docker，请参照 [docs/INSTALL.md](../docs/INSTALL.md)。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| docker-compose.yml | 编排文件 |
| Dockerfile.backend | 后端镜像 |
| Dockerfile.frontend | 前端镜像 |
| nginx.conf | Nginx 配置（前端静态文件 + API 代理） |
| init_db.sql | 数据库初始化脚本（19表 + 内置数据） |
| dump_db.py | 数据库导出工具（开发用） |

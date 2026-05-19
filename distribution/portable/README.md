# 便携式部署方案（SQLite）

> 无需 MySQL 数据库，使用 SQLite 作为后端存储，适合个人使用或小规模部署。

## 前置要求

- Python 3.10+ 已安装
- 约 500MB 磁盘空间

## 快速启动

### Windows

双击 `启动平台.bat`，脚本会自动：
1. 创建 Python 虚拟环境
2. 安装依赖包
3. 初始化 SQLite 数据库
4. 启动后端服务

### Linux/Mac

```bash
chmod +x start.sh
./start.sh
```

## 访问平台

启动后浏览器访问：**http://localhost:5173**

## 说明

- 本方案使用 SQLite 数据库，数据存储在 `backend/data/desensitization.db`
- 上传文件存储在 `uploads/` 目录
- 如需迁移到 MySQL，可参考 `deploy/init_db.sql` 创建表结构

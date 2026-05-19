# Docker 一键部署方案（推荐）

> 将整个平台（前端 + 后端 + 数据库）打包为 Docker 容器，一键启动。

## 使用方法

### Windows

1. 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. 双击运行 `一键部署.bat`

### Linux / Mac

```bash
chmod +x deploy.sh
./deploy.sh
```

## 访问地址

- 平台页面：http://localhost:8080
- API 文档：http://localhost:8000/api/docs

## 常用命令

```bash
# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 重启服务
docker compose restart
```

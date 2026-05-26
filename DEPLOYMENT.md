# Admin Agent Docker 部署指南

本文档说明如何使用 Docker 安装、启动、验证和维护 Admin Agent。默认使用 Docker Compose v2 命令 `docker compose`；如果使用旧版 Docker Compose，可以替换为 `docker-compose`。

## 快速准备

1. 安装 Docker Desktop 或 Docker Engine。

2. 验证 Docker：

   ```bash
   docker --version
   docker compose version
   ```

3. 准备环境变量：

   ```bash
   cp .env.example .env
   ```

4. 按环境修改 `.env`：

   - `SECRET_KEY`：生产环境必须替换。
   - `OPENAI_API_KEY`：需要智能助手功能时填写。
   - `FRONTEND_HOST_PORT`：开发前端端口，默认 `3000`。
   - `BACKEND_HOST_PORT`：开发后端端口，默认 `8030`。
   - `WEB_PORT`：生产单入口端口，默认 `8030`。
   - `POSTGRES_PASSWORD`：生产环境必须替换。

## 开发演示模式

开发演示模式使用 `docker-compose.yml`，包含 PostgreSQL、Redis、后端和 Vite 前端。前端、后端分别暴露端口，适合本机调试和局域网演示。

```bash
docker compose up -d --build
```

访问地址：

- 前端页面：http://localhost:3000/
- 后端健康检查：http://localhost:8030/health
- API 文档：http://localhost:8030/docs
- OpenAPI JSON：http://localhost:8030/openapi.json

查看状态和日志：

```bash
docker compose ps
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
```

停止开发环境：

```bash
docker compose down
```

如果需要清空数据库和 Redis 数据卷：

```bash
docker compose down -v
```

## 生产部署模式

生产部署模式使用 `docker-compose.prod.yml`，包含 PostgreSQL、Redis、后端和 nginx 前端容器。宿主机只暴露一个 Web 入口端口，nginx 会把 `/api`、`/docs`、`/redoc`、`/openapi.json` 代理到后端容器。

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

默认访问地址：

- 应用入口：http://localhost:8030/
- API 文档：http://localhost:8030/docs
- OpenAPI JSON：http://localhost:8030/openapi.json

如需修改生产入口端口，设置 `.env`：

```env
WEB_PORT=8080
```

然后重新启动：

```bash
docker compose -f docker-compose.prod.yml up -d
```

生产日志：

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend-nginx
```

停止生产环境：

```bash
docker compose -f docker-compose.prod.yml down
```

清空生产数据卷：

```bash
docker compose -f docker-compose.prod.yml down -v
```

## 局域网访问

查看服务器 IPv4：

```bash
ipconfig      # Windows
ip addr       # Linux
```

同一局域网设备访问：

```text
http://<服务器IPv4>:3000/   # 开发演示前端
http://<服务器IPv4>:8030/   # 生产入口或开发后端
```

如果局域网无法访问，请确认：

- Compose 端口映射已经启用。
- Windows 防火墙、Linux 防火墙或云服务器安全组已放行对应端口。
- 访问的是服务器局域网 IPv4，而不是容器内网 IP。

## 常用运维命令

开发模式：

```bash
docker compose ps
docker compose logs -f
docker compose restart
docker compose down
docker compose down -v
docker compose build --no-cache
```

生产模式：

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml restart
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml build --no-cache
```

更新代码后重新构建：

```bash
docker compose up -d --build
docker compose -f docker-compose.prod.yml up -d --build
```

可选启动 pgAdmin：

```bash
docker compose --profile tools up -d pgadmin
```

默认地址：http://localhost:5050/

## 配置校验

启动前可以先检查 Compose 配置是否能正确展开：

```bash
docker compose config
docker compose -f docker-compose.prod.yml config
```

## 健康检查

开发模式：

```bash
curl http://localhost:8030/health
curl http://localhost:8030/openapi.json
```

生产模式：

```bash
curl http://localhost:8030/
curl http://localhost:8030/openapi.json
```

## 数据备份与恢复

备份 PostgreSQL：

```bash
docker compose exec postgres pg_dump -U admin admin_agent > backup.sql
```

恢复 PostgreSQL：

```bash
docker compose exec -T postgres psql -U admin admin_agent < backup.sql
```

生产模式使用：

```bash
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U admin admin_agent > backup.sql
docker compose -f docker-compose.prod.yml exec -T postgres psql -U admin admin_agent < backup.sql
```

## 故障排查

### 端口被占用

查看占用端口：

```bash
netstat -ano | findstr :8030   # Windows
lsof -i :8030                  # Linux/macOS
```

修改 `.env` 中的端口后重启：

```env
FRONTEND_HOST_PORT=3001
BACKEND_HOST_PORT=8031
WEB_PORT=8031
```

### 环境变量缺失

如果 Compose 提示变量为空，确认根目录存在 `.env`：

```bash
cp .env.example .env
```

生产环境至少应替换：

- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `OPENAI_API_KEY`，如果需要智能助手功能

### 数据库没有就绪

查看数据库状态和日志：

```bash
docker compose ps postgres
docker compose logs -f postgres
```

重启数据库：

```bash
docker compose restart postgres
```

如果是首次开发环境并且需要重建数据：

```bash
docker compose down -v
docker compose up -d --build
```

### 健康检查失败

查看后端日志：

```bash
docker compose logs -f backend
```

常见原因：

- `DATABASE_URL` 或 PostgreSQL 密码不一致。
- 后端镜像未重建，仍在使用旧依赖。
- 端口映射被其他进程占用。
- `SECRET_KEY` 使用默认值时生产环境会有警告，应替换为随机值。

无缓存重建：

```bash
docker compose build --no-cache backend
docker compose up -d
```

## 安全建议

- 不要提交 `.env`。
- 生产环境必须替换默认密钥和数据库密码。
- 生产环境建议通过 HTTPS 反向代理对外提供服务。
- 定期备份 PostgreSQL 数据卷。
- 定期更新基础镜像和依赖。

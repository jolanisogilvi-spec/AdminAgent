# Admin Agent 行政智能体

Admin Agent 是一个面向企业行政、后勤和办公支持团队的内部管理系统。项目采用 FastAPI 后端和 React 前端，覆盖登录认证、智能助手、工单管理、审批中心、任务看板、资产管理、用户管理、知识库、系统设置和中文 API 文档。

默认登录账号：

```text
用户名：admin
密码：admin123
```

## Docker 快速安装

推荐使用 Docker Compose v2，也就是 `docker compose` 命令。旧版 Docker Compose 可以把命令替换为 `docker-compose`。

### 1. 安装 Docker

安装 Docker Desktop 或 Docker Engine，并确认命令可用：

```powershell
docker --version
docker compose version
```

### 2. 准备环境变量

```powershell
copy .env.example .env
```

按需编辑 `.env`：

- `OPENAI_API_KEY`：智能助手需要的模型 API Key。
- `SECRET_KEY`：生产环境必须替换为随机密钥。
- `FRONTEND_HOST_PORT`：开发前端端口，默认 `3000`。
- `BACKEND_HOST_PORT`：开发后端端口，默认 `8030`。
- `WEB_PORT`：生产单入口端口，默认 `8030`。
- `POSTGRES_HOST_PORT` / `REDIS_HOST_PORT`：数据库和缓存暴露端口，默认 `5432` / `6379`。

### 3. 开发演示模式

开发演示模式会启动 PostgreSQL、Redis、FastAPI 后端和 Vite 前端：

```powershell
docker compose up -d --build
```

访问地址：

- 前端页面：http://localhost:3000/
- 后端健康检查：http://localhost:8030/health
- 中文 API 文档：http://localhost:8030/docs
- OpenAPI JSON：http://localhost:8030/openapi.json

如果端口被占用，修改 `.env` 中的 `FRONTEND_HOST_PORT` 或 `BACKEND_HOST_PORT` 后重新启动。

### 4. 生产部署模式

生产模式会构建前端静态资源，由 nginx 容器提供单入口访问，并将 API 请求代理到后端容器：

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

默认访问地址：

- 应用入口：http://localhost:8030/
- API 文档：http://localhost:8030/docs
- OpenAPI JSON：http://localhost:8030/openapi.json

如需换端口，修改 `.env` 中的 `WEB_PORT`。

### 5. 局域网访问

先查看本机 IPv4 地址：

```powershell
ipconfig
```

同一局域网设备可以使用：

```text
http://<本机IPv4>:3000/   # 开发演示前端
http://<本机IPv4>:8030/   # 生产单入口或后端
```

如果无法访问，请确认 Windows 防火墙或服务器安全组已放行对应端口。

### 6. 常用 Docker 命令

```powershell
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend

# 重启服务
docker compose restart

# 停止服务，保留数据卷
docker compose down

# 停止服务并删除数据卷
docker compose down -v

# 不使用缓存重建
docker compose build --no-cache
```

生产模式把命令中的 `docker compose` 替换为：

```powershell
docker compose -f docker-compose.prod.yml
```

可选启动 pgAdmin：

```powershell
docker compose --profile tools up -d pgadmin
```

pgAdmin 默认地址：http://localhost:5050/

## 本地开发启动

如果不使用 Docker，也可以直接启动后端。后端会托管 `frontend/dist` 中的前端构建产物：

```powershell
cd E:\agent\AdminAgent\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8030
```

访问地址：

- 前端页面：http://localhost:8030/
- 健康检查：http://localhost:8030/health
- 中文 API 文档：http://localhost:8030/docs

单独调试前端：

```powershell
cd E:\agent\AdminAgent\frontend
npm install --legacy-peer-deps
npm run dev
```

构建前端：

```powershell
cd E:\agent\AdminAgent\frontend
npm run build
```

## 技术栈

后端：

- FastAPI
- Uvicorn
- SQLModel / SQLAlchemy
- Pydantic
- JWT 登录认证
- SQLite / PostgreSQL
- Redis 兼容缓存层
- Chroma 向量检索
- OpenAI 协议风格 AI 服务

前端：

- React
- TypeScript
- Vite
- Ant Design
- TanStack Query
- Zustand
- Axios

## 项目结构

```text
AdminAgent/
├─ backend/
│  ├─ app/
│  │  ├─ api/       # API 路由
│  │  ├─ core/      # 配置、数据库、安全、OpenAPI 文档
│  │  ├─ models/    # 数据模型
│  │  ├─ schemas/   # 请求和响应模型
│  │  └─ services/  # 业务服务
│  ├─ Dockerfile
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  ├─ Dockerfile
│  └─ nginx.conf
├─ docker-compose.yml
├─ docker-compose.prod.yml
└─ README.md
```

## 常用验证命令

```powershell
docker compose config
docker compose -f docker-compose.prod.yml config
python -m compileall -q backend\app

cd frontend
npm run lint
npm run build
```

## 相关文档

- [项目完整文档](./项目完整文档.md)
- [后端文档](./backend/README.md)
- [前端文档](./frontend/README.md)
- [部署文档](./DEPLOYMENT.md)
- [测试文档](./TESTING.md)

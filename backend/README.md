# Admin Agent - 后端服务

基于 FastAPI 的行政智能体后端 API 服务。

## 技术栈

- **FastAPI** - 高性能异步 Web 框架
- **SQLModel** - ORM（基于 SQLAlchemy + Pydantic）
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和会话存储
- **Uvicorn** - ASGI 服务器

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── core/                # 核心配置
│   │   ├── config.py        # 环境变量配置
│   │   ├── database.py      # 数据库连接
│   │   ├── redis.py         # Redis 客户端
│   │   └── logging.py       # 日志配置
│   ├── models/              # SQLModel 数据模型
│   │   ├── user.py
│   │   ├── ticket.py
│   │   ├── asset.py
│   │   └── enums.py
│   ├── schemas/             # Pydantic 请求/响应模型
│   ├── api/                 # API 路由
│   │   └── v1/
│   ├── services/            # 业务逻辑层
│   └── utils/               # 工具函数
├── alembic/                 # 数据库迁移
├── tests/                   # 单元测试
├── requirements.txt         # Python 依赖
├── .env.example             # 环境变量模板
└── start.sh                 # 启动脚本
```

## 快速开始

### 1. 环境准备

```bash
# 安装 Python 3.11+
python3 --version

# 安装 Docker（用于数据库）
docker --version
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis、OpenAI API Key 等
```

### 3. 启动服务

#### 方式一：使用启动脚本（推荐）

```bash
chmod +x start.sh
./start.sh
```

#### 方式二：手动启动

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动数据库和 Redis
cd ..
docker-compose up -d postgres redis
cd backend

# 4. 启动应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问服务

- **API 文档**: http://localhost:8000/api/docs
- **健康检查**: http://localhost:8000/health
- **根路径**: http://localhost:8000/

## 核心功能

### 已完成

✅ **基础设施**
- FastAPI 应用框架
- PostgreSQL 数据库连接（连接池）
- Redis 缓存集成（异步客户端）
- 环境变量管理（pydantic-settings）
- 日志系统（文件 + 控制台）
- CORS 中间件
- 健康检查接口
- Docker Compose 配置

✅ **数据模型**
- User（用户）
- Ticket（工单）
- Asset（资产）
- 枚举类型定义

### 待开发

⏳ **认证与授权**
- JWT 令牌生成与验证
- 密码哈希（bcrypt）
- RBAC 权限控制

⏳ **业务接口**
- 用户管理 API
- 工单管理 API
- 资产管理 API
- AI 智能体接口
- 审批流程 API
- 数据分析 API

⏳ **AI 集成**
- OpenAI 客户端封装
- 意图识别
- 知识库检索
- 多模态工单解析

## 配置说明

### 数据库配置

```env
DATABASE_URL=postgresql://admin:password@localhost:5432/admin_agent
```

### Redis 配置

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### JWT 配置

```env
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### OpenAI 配置

```env
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

## 开发指南

### 添加新的 API 路由

1. 在 `app/api/v1/` 创建路由文件
2. 在 `app/main.py` 中注册路由

```python
from app.api.v1 import users

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"]
)
```

### 数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 运行测试

```bash
pytest tests/ -v
```

## 依赖服务

### PostgreSQL

```bash
# 使用 Docker
docker-compose up -d postgres

# 连接数据库
psql -h localhost -U admin -d admin_agent
```

### Redis

```bash
# 使用 Docker
docker-compose up -d redis

# 连接 Redis
redis-cli -h localhost -p 6379
```

## 性能优化

- ✅ 数据库连接池（pool_size=20）
- ✅ Redis 异步客户端
- ✅ 异步 IO 操作
- ⏳ 查询优化（索引、预加载）
- ⏳ 响应缓存

## 安全措施

- ✅ 环境变量管理敏感信息
- ✅ CORS 配置
- ⏳ JWT 认证
- ⏳ 密码哈希
- ⏳ SQL 注入防护（SQLModel ORM）
- ⏳ 请求限流

## 故障排查

### 数据库连接失败

```bash
# 检查 PostgreSQL 是否运行
docker ps | grep postgres

# 查看日志
docker logs admin_agent_postgres
```

### Redis 连接失败

```bash
# 检查 Redis 是否运行
docker ps | grep redis

# 测试连接
redis-cli -h localhost -p 6379 ping
```

## 贡献指南

1. 遵循 PEP 8 代码规范
2. 使用类型注解
3. 编写单元测试
4. 更新文档

## 许可证

MIT License

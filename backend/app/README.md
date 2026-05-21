# Admin Agent Backend - FastAPI

行政智能体后端API服务 - 基于FastAPI + SQLModel + PostgreSQL

## 技术栈

- **框架**: FastAPI 0.109
- **ORM**: SQLModel 0.0.14
- **数据库**: PostgreSQL 15+
- **认证**: JWT (python-jose)
- **密码**: bcrypt (passlib)
- **缓存**: Redis
- **AI**: OpenAI Python SDK
- **向量库**: ChromaDB

## 项目结构

```
app/
├── main.py                 # FastAPI应用入口
├── core/                   # 核心配置
│   ├── config.py          # 环境配置
│   ├── database.py        # 数据库连接
│   └── security.py        # JWT和密码处理
├── models/                 # SQLModel数据模型
│   ├── user.py
│   ├── ticket.py
│   ├── asset.py
│   ├── task.py
│   └── enums.py
├── schemas/                # Pydantic请求/响应模型
├── api/                    # API路由 (待实现)
│   └── v1/
│       ├── auth.py
│       ├── users.py
│       ├── tickets.py
│       └── assets.py
├── services/               # 业务逻辑层 (待实现)
└── requirements.txt        # Python依赖
```

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 http://localhost:8000 启动

API文档:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 数据库模型

已定义的核心模型：

- **User**: 用户表（username, role, department等）
- **Ticket**: 工单表（type, status, urgency等）
- **Asset**: 资产表（category, status, stock等）
- **Task**: 任务表（关联工单）
- **ApprovalRecord**: 审批记录
- **KnowledgeBase**: 知识库
- **SysConfig**: 系统配置

## API端点

### 当前可用
- `GET /` - 根路径，返回API信息
- `GET /health` - 健康检查

### 待实现
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `GET /api/v1/users/me` - 获取当前用户信息
- `POST /api/v1/tickets` - 创建工单
- `GET /api/v1/tickets` - 查询工单列表
- 更多...

## 开发命令

```bash
# 启动开发服务器（热重载）
uvicorn app.main:app --reload

# 生产环境启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 数据库迁移（使用Alembic）
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | PostgreSQL连接字符串 | postgresql://admin:password@localhost:5432/admin_agent |
| SECRET_KEY | JWT密钥 | - |
| REDIS_HOST | Redis主机 | localhost |
| REDIS_PORT | Redis端口 | 6379 |
| OPENAI_API_KEY | OpenAI API密钥 | - |

## 下一步

1. 实现认证API（登录/注册）
2. 实现用户管理API
3. 实现工单管理API
4. 实现资产管理API
5. 集成Redis缓存
6. 集成OpenAI和ChromaDB

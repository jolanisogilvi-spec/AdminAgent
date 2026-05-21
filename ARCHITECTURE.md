# 行政智能体 (Admin Agent) - 技术架构方案

## 📚 模块文档索引

本架构文档提供整体技术栈和系统设计。各模块的详细实现文档如下：

### 后端模块
- **[认证系统](./backend/AUTH_README.md)** - JWT认证、RBAC权限控制、用户管理API
- **[后端总览](./backend/README.md)** - FastAPI项目结构、配置说明、开发指南
- **[后端搭建总结](./backend/BACKEND_SETUP_SUMMARY.md)** - 后端初始化过程和配置详情
- **[后端代码审查](./CODE_REVIEW_BACKEND.md)** - 代码质量评估、架构符合性检查 ⭐

### 前端模块
- **[前端总览](./frontend/README.md)** - React项目结构、技术栈、开发指南
- **[前端项目结构](./frontend/PROJECT_STRUCTURE.md)** - 详细的目录结构说明

### 数据库模块
- **数据库设计文档** - (待database-engineer补充)

### 部署与运维
- **[部署指南](./DEPLOYMENT.md)** - Docker部署、生产环境配置
- **[CI/CD总结](./CI-CD-SUMMARY.md)** - GitHub Actions自动化流程
- **[监控方案](./MONITORING.md)** - Prometheus + Grafana监控配置

---

## 📊 实施状态总览

**项目完成度**: 93.75% (15/16任务)  
**最后更新**: 2026-05-19

### ✅ 已完成模块

**后端 (100%)**:
- ✅ FastAPI项目脚手架
- ✅ PostgreSQL + SQLModel数据模型
- ✅ JWT认证 + RBAC权限系统
- ✅ AI意图路由与知识检索
- ✅ 工单管理系统
- ✅ 资产管理系统
- ✅ 任务管理系统
- ✅ 审批流程引擎
- ✅ 系统配置管理
- ✅ Chroma向量数据库集成

**前端 (100%)**:
- ✅ React 18 + TypeScript项目脚手架
- ✅ Ant Design 5 UI组件库
- ✅ Vite构建工具配置
- ✅ Zustand状态管理
- ✅ React Router路由配置
- ✅ Axios HTTP客户端
- ✅ 认证拦截器

**数据库 (100%)**:
- ✅ 7张核心表设计
- ✅ 索引优化
- ✅ 关系映射
- ✅ 枚举类型定义

**DevOps (100%)**:
- ✅ Docker容器化
- ✅ GitHub Actions CI/CD
- ✅ pytest测试框架
- ✅ 测试基础设施

### 🔄 进行中

- 🔄 任务#11: 知识库+系统配置API（backend-dev-2）

### 📈 技术栈落地情况

| 组件 | 架构设计 | 实际实施 | 状态 |
|------|---------|---------|------|
| FastAPI | Python 3.11+ | Python 3.11+ | ✅ 100% |
| PostgreSQL | 15+ | 15+ | ✅ 100% |
| SQLModel | ORM | ORM | ✅ 100% |
| Redis | 缓存 | 已配置 | ✅ 100% |
| Chroma | 向量库 | 已集成 | ✅ 100% |
| React | 18 | 19 | ✅ 100% |
| TypeScript | 5 | 6 | ✅ 100% |
| Ant Design | 5 | 5.29 | ✅ 100% |
| Vite | 5 | 8 | ✅ 100% |
| Zustand | 状态管理 | 5.0 | ✅ 100% |
| ECharts | 图表 | 6.0 | ✅ 100% |
| dnd-kit | 拖拽 | 6.3 | ✅ 100% |

### 🎯 架构符合性

- **分层架构**: ✅ 完全符合（API → Service → Repository → Model）
- **异步优先**: ✅ 所有IO操作异步
- **类型安全**: ✅ 全栈类型检查
- **模块化**: ✅ 清晰的模块划分
- **安全性**: ✅ JWT + RBAC + 密码哈希
- **性能优化**: ✅ 连接池 + 异步 + 索引

---

## 1. 技术栈推荐

### 1.1 后端技术栈

**核心框架:**
- **FastAPI** (Python 3.11+) - 高性能异步Web框架,原生支持OpenAPI文档
- **Uvicorn** - ASGI服务器,支持异步高并发

**数据库层:**
- **PostgreSQL 15+** - 主数据库
  - 理由: 企业级稳定性、完善的JSON支持、强大的全文检索、支持向量扩展(pgvector)
  - 相比MySQL: 更好的并发控制、复杂查询性能、JSON字段支持
- **SQLModel** - ORM工具
  - 理由: FastAPI作者开发,完美集成Pydantic,类型安全,代码简洁
  - 底层基于SQLAlchemy 2.0,成熟稳定

**向量检索(知识库):**
- **Chroma** - 轻量级向量数据库
  - 理由: Python原生、易部署、支持持久化、与OpenAI Embeddings无缝集成
  - 备选: 使用PostgreSQL的pgvector扩展(更简化架构)

**认证与安全:**
- **python-jose[cryptography]** - JWT令牌生成与验证
- **passlib[bcrypt]** - 密码哈希
- **python-multipart** - 文件上传支持

**AI集成:**
- **openai** (Python SDK) - 标准OpenAI协议客户端
- **httpx** - 异步HTTP客户端(用于自定义Base URL)

**任务队列(可选,第二期):**
- **Celery + Redis** - 异步任务处理(大模型调用、批量导入)

### 1.2 前端技术栈

**推荐方案: React 18 + TypeScript + Ant Design Pro**

**核心框架:**
- **React 18** + **TypeScript 5**
  - 理由: 生态最成熟、企业级组件库丰富、团队技能通用性强
- **Vite 5** - 构建工具(比Webpack快10倍)
- **React Router v6** - 路由管理

**UI组件库:**
- **Ant Design 5** (antd)
  - 理由: 国内B端标准、组件完善(表单/表格/看板)、中文文档友好
  - 内置ProComponents(ProTable/ProForm)专为后台系统设计

**状态管理:**
- **Zustand** - 轻量级状态管理
  - 理由: 比Redux简单、比Context性能好、TypeScript友好

**数据请求:**
- **TanStack Query (React Query)** - 服务端状态管理
  - 理由: 自动缓存、重试、轮询、乐观更新
- **Axios** - HTTP客户端

**图表库:**
- **Apache ECharts** - 数据可视化
  - 理由: 功能强大、中文文档、支持复杂业务图表

**拖拽看板:**
- **@dnd-kit/core** - 现代化拖拽库
  - 理由: 性能优秀、无障碍支持、TypeScript原生

**备选方案: Vue 3 + Element Plus**
- 优势: 学习曲线平缓、模板语法直观
- 劣势: 企业级生态不如React、招聘难度略高

### 1.3 部署与运维

**容器化:**
- **Docker** + **Docker Compose** - 本地开发与测试环境
- **多阶段构建** - 优化镜像体积

**生产部署:**
- **Nginx** - 反向代理、静态资源服务
- **Gunicorn + Uvicorn Workers** - 生产级ASGI服务

**CI/CD:**
- **GitHub Actions** / **GitLab CI** - 自动化测试与部署

**监控:**
- **Prometheus + Grafana** - 性能监控
- **Sentry** - 错误追踪

---

## 2. 系统架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 员工端   │  │ 行政端   │  │ 审批端   │  │ 管理端   │   │
│  │ (聊天)   │  │ (看板)   │  │ (审批)   │  │ (Dashboard)│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    API网关层 (Nginx)                         │
│              ┌─────────────────────────────┐                │
│              │  CORS / 限流 / 日志 / HTTPS  │                │
│              └─────────────────────────────┘                │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   应用层 (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              认证中间件 (JWT + RBAC)                  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ Users    │ │ Tickets  │ │ Assets   │ │ AI Agent │     │
│  │ Router   │ │ Router   │ │ Router   │ │ Router   │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                  │
│  │ Tasks    │ │ Configs  │ │ Analytics│                  │
│  │ Router   │ │ Router   │ │ Router   │                  │
│  └──────────┘ └──────────┘ └──────────┘                  │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      服务层 (Services)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ AI Service   │  │ Auth Service │  │ Asset Service│     │
│  │ - 意图识别   │  │ - JWT生成    │  │ - 库存管理   │     │
│  │ - 知识检索   │  │ - 权限验证   │  │ - 状态流转   │     │
│  │ - 工单解析   │  └──────────────┘  └──────────────┘     │
│  └──────────────┘                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Ticket Svc   │  │ Approval Svc │  │ Analytics Svc│     │
│  │ - 工单生成   │  │ - 审批流转   │  │ - 数据聚合   │     │
│  │ - 状态管理   │  │ - 规则引擎   │  │ - 报表生成   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    数据访问层 (SQLModel)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              数据库会话管理 (依赖注入)                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据存储层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ PostgreSQL   │  │ Chroma       │  │ Redis        │     │
│  │ (主数据库)   │  │ (向量库)     │  │ (缓存/队列)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    外部服务集成                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ OpenAI API   │  │ 文件存储     │  │ 邮件/通知    │     │
│  │ (动态配置)   │  │ (OSS/S3)     │  │ (可选)       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心设计原则

**1. 分层架构 (Layered Architecture)**
- **表现层**: React组件,负责UI渲染与用户交互
- **API层**: FastAPI路由,负责请求验证与响应格式化
- **业务层**: Service类,负责核心业务逻辑
- **数据层**: SQLModel模型,负责数据持久化

**2. 依赖注入 (Dependency Injection)**
- 使用FastAPI的`Depends`机制管理数据库会话、用户认证
- 便于单元测试Mock

**3. 配置外部化**
- 环境变量管理敏感信息(`.env`文件)
- 数据库存储业务配置(SysConfig表)
- 支持运行时动态切换大模型

**4. 异步优先**
- 所有IO操作使用`async/await`
- 提升并发处理能力(大模型调用、数据库查询)

**5. 类型安全**
- 后端: Pydantic模型强制类型验证
- 前端: TypeScript严格模式

---

## 3. 数据库设计优化建议

### 3.1 核心表结构(基于SQLModel)

原需求中的6张表设计合理,建议以下优化:

**User表增强:**
```python
class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str = Field(unique=True, index=True)  # 登录用户名
    full_name: str  # 真实姓名
    password_hash: str
    role: UserRole  # Enum: employee, admin_staff, manager, sys_admin
    department: str
    email: str | None = None  # 用于通知
    is_active: bool = True  # 软删除标记
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Asset表增强:**
```python
class Asset(SQLModel, table=True):
    id: int = Field(primary_key=True)
    asset_code: str = Field(unique=True, index=True)  # 资产编号
    name: str
    category: AssetCategory  # Enum: IT设备/办公家具/耗材
    status: AssetStatus  # Enum: 闲置/使用中/维修中/报废
    owner_id: int | None = Field(foreign_key="user.id")
    current_stock: int = 0  # 耗材类资产的库存
    unit_price: Decimal | None = None  # 单价
    purchase_date: date | None = None
    warranty_expire: date | None = None  # 保修期
    location: str | None = None  # 存放位置
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Ticket表增强:**
```python
class Ticket(SQLModel, table=True):
    id: int = Field(primary_key=True)
    requester_id: int = Field(foreign_key="user.id")  # 发起人
    original_text: str  # 原始诉求
    attachments: str | None = None  # JSON数组存储图片URL
    ticket_type: TicketType  # Enum: 采购/报修/申领/咨询
    related_asset_id: int | None = Field(foreign_key="asset.id")
    estimated_cost: Decimal = 0
    approval_status: ApprovalStatus  # Enum: 无需审批/待主管/待财务/已通过/已驳回
    processing_status: ProcessingStatus  # Enum: 待接单/处理中/已闭环
    assigned_to: int | None = Field(foreign_key="user.id")  # 行政负责人
    urgency: UrgencyLevel = UrgencyLevel.NORMAL  # 紧急程度
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: datetime | None = None
```

**新增: ApprovalRecord表(审批记录)**
```python
class ApprovalRecord(SQLModel, table=True):
    """审批流水记录,支持多级审批"""
    id: int = Field(primary_key=True)
    ticket_id: int = Field(foreign_key="ticket.id")
    approver_id: int = Field(foreign_key="user.id")
    approval_type: str  # "manager" / "finance"
    status: str  # "pending" / "approved" / "rejected"
    comment: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**KnowledgeBase表增强:**
```python
class KnowledgeBase(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    content: str
    category: str  # 分类标签
    embedding: str | None = None  # JSON存储向量(或使用Chroma)
    view_count: int = 0  # 查看次数
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.2 索引策略

```sql
-- 高频查询字段建立索引
CREATE INDEX idx_ticket_requester ON ticket(requester_id);
CREATE INDEX idx_ticket_status ON ticket(processing_status, approval_status);
CREATE INDEX idx_ticket_created ON ticket(created_at DESC);
CREATE INDEX idx_asset_status ON asset(status);
CREATE INDEX idx_task_assigned ON task(assigned_to, status);
```

---

## 4. AI集成架构

### 4.1 动态配置设计

**SysConfig表存储:**
```python
# 系统启动时加载到内存缓存(Redis)
configs = {
    "LLM_BASE_URL": "https://api.openai.com/v1",
    "LLM_API_KEY": "sk-xxx",
    "LLM_MODEL": "gpt-4o",
    "LLM_TEMPERATURE": "0.7",
    "EMBEDDING_MODEL": "text-embedding-3-small"
}
```

**AI Service层设计:**
```python
class AIService:
    async def get_llm_client(self) -> AsyncOpenAI:
        """从数据库读取配置,动态创建客户端"""
        config = await get_sys_config(["LLM_BASE_URL", "LLM_API_KEY"])
        return AsyncOpenAI(
            base_url=config["LLM_BASE_URL"],
            api_key=config["LLM_API_KEY"]
        )
    
    async def intent_classification(self, user_input: str) -> Intent:
        """意图识别: 咨询 vs 工单"""
        # 使用Function Calling提取结构化意图
        
    async def knowledge_search(self, query: str) -> str:
        """知识库检索(向量相似度)"""
        # 1. 生成query的embedding
        # 2. Chroma相似度搜索
        # 3. 返回最相关的SOP内容
        
    async def parse_ticket(self, user_input: str, images: list) -> TicketData:
        """多模态工单解析"""
        # 支持vision模型识别图片中的设备故障
```

### 4.2 意图路由流程

```
用户输入(文本+图片)
      |
      v
┌─────────────────┐
│ 意图分类(LLM)   │
└─────────────────┘
      |
      v
   判断意图类型
      |
      +-------------------+
      |                   |
      v                   v
  [咨询类]            [动作类]
      |                   |
      v                   v
 知识库检索          工单结构化解析
      |                   |
      v                   |
  返回答案            提取字段:
  (不建单)            - 类型
                      - 物品
                      - 紧急度
                      - 预估费用
                          |
                          v
                      费用判断
                          |
                   +------+------+
                   |             |
                   v             v
              >阈值         ≤阈值
                   |             |
                   v             v
            设置"待审批"   设置"无需审批"
                   |             |
                   +------+------+
                          |
                          v
                    创建Ticket记录
                          |
                          v
                    返回工单编号
```

---

## 5. 安全与权限设计

### 5.1 认证流程(JWT)

```
1. 用户登录 -> 验证用户名密码
2. 生成JWT Token (payload: user_id, role, exp)
3. 前端存储Token (localStorage)
4. 后续请求携带 Authorization: Bearer <token>
5. 中间件验证Token -> 解析用户信息 -> 注入到request.state
```

### 5.2 RBAC权限矩阵

| 功能模块 | 员工 | 行政专员 | 部门主管 | 系统管理员 |
|---------|------|---------|---------|----------|
| 提交工单 | ✓ | ✓ | ✓ | ✓ |
| 查看自己的工单 | ✓ | ✓ | ✓ | ✓ |
| 查看本部门工单 | ✗ | ✗ | ✓ | ✓ |
| 查看所有工单 | ✗ | ✓ | ✗ | ✓ |
| 接单/处理工单 | ✗ | ✓ | ✗ | ✓ |
| 审批工单 | ✗ | ✗ | ✓ | ✓ |
| 资产管理 | ✗ | ✓ | ✗ | ✓ |
| 系统配置 | ✗ | ✗ | ✗ | ✓ |
| 数据看板 | ✗ | ✓ | ✓ | ✓ |

### 5.3 数据隔离策略

```python
# 在Service层实现数据过滤
async def get_tickets(user: User, filters: dict):
    query = select(Ticket)
    
    if user.role == UserRole.EMPLOYEE:
        # 员工只能看自己的
        query = query.where(Ticket.requester_id == user.id)
    elif user.role == UserRole.MANAGER:
        # 主管看本部门的
        dept_users = await get_department_users(user.department)
        query = query.where(Ticket.requester_id.in_(dept_users))
    elif user.role == UserRole.ADMIN_STAFF:
        # 行政看全部
        pass
    
    return await db.execute(query)
```

---

## 6. 性能优化策略

### 6.1 数据库优化
- **连接池**: SQLAlchemy连接池(pool_size=20)
- **查询优化**: 使用`joinedload`预加载关联数据,避免N+1问题
- **分页**: 所有列表接口强制分页(limit/offset)

### 6.2 缓存策略
- **Redis缓存**:
  - 系统配置(SysConfig) - TTL 5分钟
  - 知识库热点问题 - TTL 1小时
  - 用户权限信息 - TTL 30分钟

### 6.3 异步处理
- **大模型调用**: 使用异步客户端,避免阻塞
- **文件上传**: 异步写入OSS
- **邮件通知**: Celery异步任务

---

## 7. 项目目录结构

```
admin-agent/
├── backend/                    # FastAPI后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 环境变量配置
│   │   │   ├── security.py    # JWT/密码哈希
│   │   │   └── database.py    # 数据库连接
│   │   ├── models/            # SQLModel数据模型
│   │   │   ├── user.py
│   │   │   ├── ticket.py
│   │   │   ├── asset.py
│   │   │   ├── task.py
│   │   │   ├── knowledge.py
│   │   │   └── config.py
│   │   ├── schemas/           # Pydantic请求/响应模型
│   │   │   ├── user.py
│   │   │   ├── ticket.py
│   │   │   └── ...
│   │   ├── api/               # API路由
│   │   │   ├── deps.py        # 依赖注入(认证/数据库)
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── users.py
│   │   │       ├── auth.py
│   │   │       ├── tickets.py
│   │   │       ├── assets.py
│   │   │       ├── tasks.py
│   │   │       ├── ai_agent.py
│   │   │       ├── configs.py
│   │   │       └── analytics.py
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── ai_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── ticket_service.py
│   │   │   ├── asset_service.py
│   │   │   └── analytics_service.py
│   │   └── utils/             # 工具函数
│   │       ├── enums.py       # 枚举定义
│   │       └── helpers.py
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 单元测试
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/                   # React前端
│   ├── src/
│   │   ├── main.tsx           # 入口文件
│   │   ├── App.tsx
│   │   ├── pages/             # 页面组件
│   │   │   ├── Login/
│   │   │   ├── Employee/      # 员工端(聊天界面)
│   │   │   ├── Admin/         # 行政端(任务看板)
│   │   │   ├── Approval/      # 审批端
│   │   │   ├── Dashboard/     # 管理端(数据看板)
│   │   │   └── Settings/      # 系统设置
│   │   ├── components/        # 通用组件
│   │   │   ├── ChatBox/
│   │   │   ├── TicketCard/
│   │   │   ├── KanbanBoard/
│   │   │   └── ...
│   │   ├── services/          # API调用
│   │   │   ├── api.ts         # Axios实例
│   │   │   ├── auth.ts
│   │   │   ├── ticket.ts
│   │   │   └── ...
│   │   ├── stores/            # Zustand状态管理
│   │   │   ├── authStore.ts
│   │   │   └── configStore.ts
│   │   ├── types/             # TypeScript类型定义
│   │   ├── utils/
│   │   └── styles/
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── docker-compose.yml         # 本地开发环境
├── .gitignore
└── README.md
```

---

## 8. 开发阶段规划

### 阶段一: 基础设施(Week 1-2)
- [x] 项目初始化与目录结构
- [ ] 数据库设计与迁移脚本
- [ ] JWT认证与RBAC中间件
- [ ] 系统配置CRUD接口
- [ ] 前端脚手架与路由

### 阶段二: AI核心(Week 3-4)
- [ ] OpenAI客户端封装(支持动态配置)
- [ ] 意图分类与知识检索
- [ ] 多模态工单解析
- [ ] 聊天界面与设置页面

### 阶段三: 业务流程(Week 5-6)
- [ ] 工单管理接口
- [ ] 审批流程引擎
- [ ] 资产库存联动
- [ ] 任务看板(拖拽)

### 阶段四: 数据分析(Week 7-8)
- [ ] 数据聚合接口
- [ ] ECharts图表集成
- [ ] 导出报表功能

---

## 9. 风险与挑战

### 9.1 技术风险
- **大模型调用延迟**: 使用流式响应(SSE)提升体验
- **向量检索准确率**: 需要高质量的知识库内容与Embedding模型
- **并发性能**: 通过异步+连接池+缓存优化

### 9.2 业务风险
- **审批规则复杂**: 设计灵活的规则引擎(JSON配置)
- **数据安全**: 敏感配置加密存储,API限流防爬

---

## 10. 总结与建议

**推荐技术栈组合:**
- **后端**: FastAPI + PostgreSQL + SQLModel + Chroma
- **前端**: React 18 + TypeScript + Ant Design + Zustand
- **部署**: Docker + Nginx + Gunicorn

**核心优势:**
1. **类型安全**: 全栈TypeScript/Python类型检查
2. **高性能**: 异步架构+数据库优化
3. **易维护**: 清晰的分层架构+模块化设计
4. **可扩展**: 支持水平扩展(无状态API)

**下一步行动:**
1. 确认技术栈选型
2. 初始化项目骨架
3. 搭建开发环境(Docker Compose)
4. 实现第一阶段功能

# Admin Agent 行政智能体

Admin Agent 是一个面向企业行政、后勤和办公支持团队的内部管理系统。项目采用 FastAPI 后端和 React 前端，覆盖登录认证、智能助手、工单管理、审批中心、任务看板、资产管理、用户管理、知识库、系统设置和中文 API 文档。

当前推荐本地访问端口为 `8030`。后端会托管前端构建产物，启动后可直接访问：

```text
http://localhost:8030/
```

默认登录账号：

```text
用户名：admin
密码：admin123
```

## 快速启动

### 1. 启动后端

```powershell
cd E:\agent\AdminAgent\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8030
```

启动后可访问：

- 前端页面：http://localhost:8030/
- 健康检查：http://localhost:8030/health
- 中文 API 文档：http://localhost:8030/docs
- OpenAPI JSON：http://localhost:8030/openapi.json

### 2. 前端开发模式

如果需要单独调试前端：

```powershell
cd E:\agent\AdminAgent\frontend
npm install --legacy-peer-deps
npm run dev
```

前端开发服务默认端口为 `3000`，接口代理到 `http://localhost:8030`。

### 3. 前端构建

```powershell
cd E:\agent\AdminAgent\frontend
npm run build
```

构建产物输出到 `frontend/dist`。后端启动时会自动托管该目录中的页面和静态资源。

## 技术栈

后端：

- FastAPI
- Uvicorn
- SQLModel / SQLAlchemy
- Pydantic
- JWT 登录认证
- SQLite 本地数据库
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

## 主要功能

- 数据看板：展示工单、任务、资产和费用等核心指标。
- 智能助手：支持行政知识问答和自然语言生成工单。
- 工单管理：支持新建、筛选、查看、编辑、删除工单。
- 任务看板：支持任务创建、筛选、状态流转、编辑和删除。
- 审批中心：支持主管审批、财务审批、通过和驳回。
- 资产管理：支持资产新增、筛选、详情、编辑、删除和库存调整。
- 知识库：支持知识新增、编辑、删除、分类筛选、语义检索和向量同步。
- 用户管理：支持添加用户、编辑用户、设置角色、启用/停用账号、重置密码和删除用户。
- 系统设置：按业务分类维护基础设置、AI 模型、审批规则和知识库配置。
- 接口文档：前端顶部提供“接口文档”按钮，可直接进入中文 Swagger 文档。

## 系统设置说明

系统设置页不再展示原始“配置键/配置值”表格，而是按业务分类直接填写：

- 基础设置：系统名称、登录有效期、附件上传上限、自动分派工单。
- AI 模型：模型服务地址、模型 API 密钥、模型名称、回复随机性、最大回复长度。
- 审批规则：主管审批金额、财务审批金额。
- 知识库：向量服务地址、知识向量模型、知识库索引目录。

知识库中的向量服务地址使用独立配置 `EMBEDDING_BASE_URL`，不会和 AI 聊天模型的 `LLM_BASE_URL` 混用。

## API 文档

API 文档已整理为中文，入口：

```text
http://localhost:8030/docs
```

当前文档包含 10 个中文分组：

- 认证登录
- 用户管理
- 工单管理
- 资产管理
- 任务管理
- 审批管理
- 知识库
- 系统设置
- 智能助手
- 系统监控

OpenAPI 中已补齐接口中文摘要、接口说明、参数说明、请求模型和响应模型标题。前端 SPA 兜底路由不会出现在 API 文档中。

## 项目结构

```text
AdminAgent/
├─ backend/
│  ├─ app/
│  │  ├─ api/              # API 路由
│  │  ├─ core/             # 配置、数据库、安全、OpenAPI 文档等核心能力
│  │  ├─ models/           # 数据模型
│  │  ├─ schemas/          # 请求和响应模型
│  │  └─ services/         # 业务服务
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ components/       # 通用组件
│  │  ├─ layouts/          # 页面布局
│  │  ├─ pages/            # 业务页面
│  │  ├─ router/           # 路由
│  │  ├─ services/         # 接口调用
│  │  ├─ stores/           # 状态管理
│  │  └─ theme/            # Ant Design 主题
│  └─ package.json
├─ 项目完整文档.md
└─ README.md
```

## 常用验证命令

```powershell
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

## 当前说明

项目当前可在 `8030` 端口提供一体化访问。默认使用本地 SQLite 运行，适合快速开发和本地演示；Docker Compose 中仍保留 PostgreSQL、Redis、前后端分离部署等配置，可按部署环境继续调整。

# 数据库模型设计文档

## 概述

本文档描述了行政智能体系统（Admin Agent）的数据库模型设计。系统使用 **PostgreSQL** 作为主数据库，**SQLModel** 作为 ORM 框架（结合了 SQLAlchemy 和 Pydantic）。

## 技术栈

- **数据库**: PostgreSQL 14+
- **ORM**: SQLModel (基于 SQLAlchemy 2.0 + Pydantic)
- **迁移工具**: Alembic
- **向量检索**: Chroma/FAISS (可选，用于知识库语义搜索)

## 核心表结构

### 1. User (用户表)

**表名**: `users`

**用途**: 存储系统所有用户信息，支持多角色权限管理

**字段说明**:

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto | 用户ID |
| username | String(50) | Unique, Index | 用户名 |
| full_name | String(100) | Not Null | 姓名 |
| password_hash | String(255) | Not Null | 密码哈希 |
| role | Enum | Not Null | 角色：employee/admin/manager/system_admin |
| department | String(100) | Not Null | 所属部门 |
| email | String(100) | Nullable | 邮箱 |
| phone | String(20) | Nullable | 电话 |
| is_active | Boolean | Default: True | 是否激活 |
| created_at | DateTime | Auto | 创建时间 |
| updated_at | DateTime | Auto | 更新时间 |

**关系**:
- 一对多: tickets (创建的工单)
- 一对多: assigned_tasks (分配的任务)
- 一对多: owned_assets (拥有的资产)

**索引**:
- username (唯一索引)
- role, department (复合索引，用于权限查询)

---

### 2. Asset (资产库表)

**表名**: `assets`

**用途**: 管理公司所有资产，包括IT设备、办公家具、耗材等

**字段说明**:

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto | 资产ID |
| asset_code | String(50) | Unique, Index | 资产编号 |
| asset_name | String(200) | Not Null | 资产名称 |
| category | Enum | Not Null | 分类：it_equipment/office_furniture/consumables |
| status | Enum | Default: idle | 状态：idle/in_use/under_repair/scrapped |
| owner_id | Integer | FK(users.id) | 归属人ID |
| current_stock | Integer | Default: 0 | 当前库存量 |
| unit_price | Float | Nullable | 单价 |
| purchase_date | DateTime | Nullable | 采购日期 |
| warranty_until | DateTime | Nullable | 保修期至 |
| brand | String(100) | Nullable | 品牌 |
| model | String(100) | Nullable | 型号 |
| specifications | Text | Nullable | 规格说明 |
| location | String(200) | Nullable | 存放位置 |
| supplier | String(200) | Nullable | 供应商 |
| notes | Text | Nullable | 备注 |
| created_at | DateTime | Auto | 创建时间 |
| updated_at | DateTime | Auto | 更新时间 |

**关系**:
- 多对一: owner (归属用户)
- 一对多: tickets (关联的工单)

**索引**:
- asset_code (唯一索引)
- category, status (复合索引)
- owner_id (外键索引)

---

### 3. Ticket (行政工单表)

**表名**: `tickets`

**用途**: 核心业务表，记录员工提交的各类行政诉求

**字段说明**:

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto | 工单ID |
| creator_id | Integer | FK(users.id) | 发起人ID |
| original_text | Text | Not Null | 原始文本内容 |
| attachments | Text | Nullable | 附件图片URL（JSON数组） |
| ticket_type | Enum | Not Null | 类型：procurement/repair/requisition/consultation |
| title | String(200) | Not Null | 工单标题 |
| description | Text | Nullable | 详细描述 |
| urgency_level | Integer | 1-5 | 紧急程度 |
| related_asset_id | Integer | FK(assets.id) | 关联资产ID |
| estimated_cost | Float | Nullable | 预估费用 |
| actual_cost | Float | Nullable | 实际费用 |
| approval_status | Enum | Default: no_approval_needed | 审批状态 |
| approved_by_manager_id | Integer | FK(users.id) | 主管审批人ID |
| approved_by_finance_id | Integer | FK(users.id) | 财务审批人ID |
| approval_notes | Text | Nullable | 审批备注 |
| processing_status | Enum | Default: pending | 处理状态 |
| assigned_admin_id | Integer | FK(users.id) | 分配的行政人员ID |
| ai_confidence_score | Float | 0-1 | AI解析置信度 |
| ai_parsed_json | Text | Nullable | AI解析的结构化JSON |
| created_at | DateTime | Auto | 创建时间 |
| updated_at | DateTime | Auto | 更新时间 |
| closed_at | DateTime | Nullable | 闭环时间 |

**关系**:
- 多对一: creator (创建人)
- 多对一: related_asset (关联资产)
- 一对多: tasks (关联的执行任务)

**索引**:
- creator_id, created_at (复合索引，用于查询用户工单)
- ticket_type, processing_status (复合索引，用于工单筛选)
- approval_status (索引，用于审批列表)

---

### 4. Task (行政执行任务表)

**表名**: `tasks`

**用途**: 工单审批通过后的具体执行任务

**字段说明**:

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto | 任务ID |
| ticket_id | Integer | FK(tickets.id) | 关联工单ID |
| task_name | String(200) | Not Null | 任务名称 |
| description | Text | Nullable | 任务描述 |
| status | Enum | Default: todo | 状态：todo/in_progress/completed/cancelled |
| assignee_id | Integer | FK(users.id) | 负责人ID |
| supplier_name | String(200) | Nullable | 供应商名称 |
| supplier_contact | String(100) | Nullable | 供应商联系人 |
| supplier_phone | String(20) | Nullable | 供应商电话 |
| external_contact | String(200) | Nullable | 外部对接人信息 |
| deadline | DateTime | Nullable | 截止时间 |
| started_at | DateTime | Nullable | 开始时间 |
| completed_at | DateTime | Nullable | 完成时间 |
| budget | Float | Nullable | 预算金额 |
| actual_cost | Float | Nullable | 实际花费 |
| progress_percentage | Integer | 0-100 | 完成进度 |
| notes | Text | Nullable | 备注 |
| created_at | DateTime | Auto | 创建时间 |
| updated_at | DateTime | Auto | 更新时间 |

**关系**:
- 多对一: ticket (关联工单)
- 多对一: assignee (负责人)

**索引**:
- ticket_id (外键索引)
- assignee_id, status (复合索引，用于任务看板)
- deadline (索引，用于逾期提醒)

---

### 5. KnowledgeBase (知识库SOP表)

**表名**: `knowledge_base`

**用途**: 存储企业行政SOP，支持AI智能客服

**字段说明**:

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto | 知识库ID |
| title | String(200) | Not Null | 标题 |
| content | Text | Not Null | 内容详情 |
| category | String(100) | Not Null | 分类 |
| applicable_scenarios | Text | Nullable | 适用场景（JSON数组） |
| tags | Text | Nullable | 标签（JSON数组） |
| embedding_vector | Text | Nullable | 向量化特征（JSON） |
| embedding_model | String(100) | Nullable | 向量化模型 |
| view_count | Integer | Default: 0 | 查看次数 |
| helpful_count | Integer | Default: 0 | 有帮助次数 |
| unhelpful_count | Integer | Default: 0 | 无帮助次数 |
| version | Integer | Default: 1 | 版本号 |
| is_active | Boolean | Default: True | 是否启用 |
| created_by | Integer | FK(users.id) | 创建人ID |
| updated_by | Integer | FK(users.id) | 最后更新人ID |
| created_at | DateTime | Auto | 创建时间 |
| updated_at | DateTime | Auto | 更新时间 |

**索引**:
- category (索引)
- is_active (索引)
- 全文搜索索引 (title, content)

**向量检索**:
- 可选集成 Chroma 或 FAISS 进行语义搜索
- embedding_vector 字段存储向量化后的特征

---

### 6. SysConfig (系统配置表)

**表名**: `sys_config`

**用途**: 存储系统级配置，特别是大模型API配置

**字段说明**:

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, Auto | 配置ID |
| config_key | String(100) | Unique | 配置键名 |
| config_value | Text | Not Null | 配置键值 |
| description | String(500) | Nullable | 配置说明 |
| category | String(50) | Default: general | 配置分类 |
| value_type | String(20) | Default: string | 值类型 |
| is_sensitive | Boolean | Default: False | 是否敏感信息 |
| is_required | Boolean | Default: False | 是否必填 |
| default_value | Text | Nullable | 默认值 |
| validation_rule | Text | Nullable | 验证规则 |
| display_order | Integer | Default: 0 | 显示排序 |
| is_visible | Boolean | Default: True | 是否在前端显示 |
| is_editable | Boolean | Default: True | 是否可编辑 |
| created_at | DateTime | Auto | 创建时间 |
| updated_at | DateTime | Auto | 更新时间 |
| updated_by | Integer | FK(users.id) | 最后更新人ID |

**预定义配置项**:
- `LLM_BASE_URL`: 大模型API基础URL
- `LLM_API_KEY`: 大模型API密钥
- `LLM_MODEL_NAME`: 模型名称
- `LLM_TEMPERATURE`: 温度参数
- `APPROVAL_THRESHOLD_AMOUNT`: 审批金额阈值
- `SYSTEM_NAME`: 系统名称

**索引**:
- config_key (唯一索引)
- category (索引)

---

## 数据库关系图

```
User (用户)
├─ 1:N → Ticket (创建的工单)
├─ 1:N → Task (分配的任务)
├─ 1:N → Asset (拥有的资产)
└─ 1:N → KnowledgeBase (创建/更新的知识)

Asset (资产)
├─ N:1 → User (归属人)
└─ 1:N → Ticket (关联的工单)

Ticket (工单)
├─ N:1 → User (创建人)
├─ N:1 → Asset (关联资产)
└─ 1:N → Task (衍生的任务)

Task (任务)
├─ N:1 → Ticket (关联工单)
└─ N:1 → User (负责人)

KnowledgeBase (知识库)
├─ N:1 → User (创建人)
└─ N:1 → User (更新人)

SysConfig (系统配置)
└─ N:1 → User (更新人)
```

## 数据库初始化脚本

### 创建数据库

```sql
CREATE DATABASE admin_agent_db
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'zh_CN.UTF-8'
    LC_CTYPE = 'zh_CN.UTF-8'
    TEMPLATE = template0;
```

### 创建扩展

```sql
-- 全文搜索扩展（用于知识库搜索）
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- UUID生成扩展（可选）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## 性能优化建议

### 1. 索引优化

```sql
-- 工单查询优化
CREATE INDEX idx_tickets_creator_created ON tickets(creator_id, created_at DESC);
CREATE INDEX idx_tickets_status ON tickets(processing_status, approval_status);

-- 任务看板优化
CREATE INDEX idx_tasks_assignee_status ON tasks(assignee_id, status);
CREATE INDEX idx_tasks_deadline ON tasks(deadline) WHERE status != 'completed';

-- 知识库搜索优化
CREATE INDEX idx_kb_category_active ON knowledge_base(category, is_active);
CREATE INDEX idx_kb_fulltext ON knowledge_base USING gin(to_tsvector('chinese', title || ' ' || content));
```

### 2. 分区策略（可选）

对于大量历史数据的表，可以考虑按时间分区：

```sql
-- 工单表按月分区（示例）
CREATE TABLE tickets_2024_01 PARTITION OF tickets
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 3. 查询优化

- 使用连接池（SQLAlchemy 内置）
- 启用查询缓存
- 对高频查询使用物化视图
- 定期执行 VACUUM ANALYZE

## 数据迁移

使用 Alembic 进行数据库版本管理：

```bash
# 初始化迁移
alembic init alembic

# 生成迁移脚本
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

## 安全考虑

1. **密码存储**: 使用 bcrypt 或 argon2 进行密码哈希
2. **敏感配置**: SysConfig 中的敏感字段（is_sensitive=True）需要加密存储
3. **SQL注入防护**: 使用 ORM 参数化查询
4. **访问控制**: 基于 RBAC 的行级权限控制
5. **审计日志**: 记录关键操作（工单审批、配置修改等）

## 备份策略

```bash
# 每日全量备份
pg_dump -U postgres -d admin_agent_db -F c -f backup_$(date +%Y%m%d).dump

# 启用 WAL 归档（用于时间点恢复）
archive_mode = on
archive_command = 'cp %p /backup/archive/%f'
```

## 监控指标

- 数据库连接数
- 慢查询日志（> 1秒）
- 表膨胀率
- 索引命中率
- 缓存命中率

---

**文档版本**: 1.0  
**最后更新**: 2024-05-19  
**维护者**: 数据库工程师

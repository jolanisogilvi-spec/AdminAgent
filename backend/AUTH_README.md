# 用户认证系统实现文档

## 概述

本模块实现了基于 JWT 的用户认证和 RBAC 权限控制系统。

## 功能特性

### 1. 用户认证
- ✅ 用户注册
- ✅ 用户登录（JWT Token）
- ✅ 密码哈希（bcrypt）
- ✅ Token 验证
- ✅ 获取当前用户信息

### 2. 权限控制（RBAC）
- ✅ 四种用户角色：
  - `employee` - 员工
  - `admin_staff` - 行政专员
  - `manager` - 部门主管
  - `sys_admin` - 系统管理员
- ✅ 基于角色的访问控制
- ✅ 灵活的权限检查器

## 文件结构

```
app/
├── models/
│   └── user.py              # User 模型和 UserRole 枚举
├── schemas/
│   └── user.py              # Pydantic 请求/响应模型
├── core/
│   └── security.py          # JWT 和密码哈希工具
├── api/
│   ├── deps.py              # 认证依赖注入
│   └── v1/
│       └── auth.py          # 认证路由
└── scripts/
    └── create_admin.py      # 创建管理员脚本
```

## API 接口

### 1. 用户注册

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "zhangsan",
  "password": "password123",
  "full_name": "张三",
  "department": "技术部",
  "email": "zhangsan@company.com",
  "role": "employee"
}
```

响应:
```json
{
  "id": 1,
  "username": "zhangsan",
  "full_name": "张三",
  "role": "employee",
  "department": "技术部",
  "email": "zhangsan@company.com",
  "is_active": true,
  "created_at": "2026-05-19T10:00:00",
  "updated_at": "2026-05-19T10:00:00"
}
```

### 2. 用户登录

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "zhangsan",
  "password": "password123"
}
```

响应:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "zhangsan",
    "full_name": "张三",
    "role": "employee",
    "department": "技术部",
    "email": "zhangsan@company.com",
    "is_active": true,
    "created_at": "2026-05-19T10:00:00",
    "updated_at": "2026-05-19T10:00:00"
  }
}
```

### 3. 获取当前用户信息

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

响应:
```json
{
  "id": 1,
  "username": "zhangsan",
  "full_name": "张三",
  "role": "employee",
  "department": "技术部",
  "email": "zhangsan@company.com",
  "is_active": true,
  "created_at": "2026-05-19T10:00:00",
  "updated_at": "2026-05-19T10:00:00"
}
```

### 4. 用户登出

```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

响应:
```json
{
  "message": "登出成功"
}
```

## 使用示例

### 1. 在路由中使用认证

```python
from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"Hello, {current_user.full_name}!"}
```

### 2. 使用角色权限检查

```python
from fastapi import APIRouter, Depends
from app.api.deps import require_admin, require_admin_or_staff
from app.models.user import User

router = APIRouter()

# 仅管理员可访问
@router.get("/admin-only")
async def admin_only(
    current_user: User = Depends(require_admin)
):
    return {"message": "Admin access granted"}

# 管理员或行政专员可访问
@router.get("/staff-access")
async def staff_access(
    current_user: User = Depends(require_admin_or_staff)
):
    return {"message": "Staff access granted"}
```

### 3. 自定义角色检查

```python
from fastapi import APIRouter, Depends
from app.api.deps import RoleChecker
from app.models.user import User, UserRole

router = APIRouter()

# 仅主管和管理员可访问
require_manager_or_admin = RoleChecker([UserRole.MANAGER, UserRole.SYS_ADMIN])

@router.get("/manager-access")
async def manager_access(
    current_user: User = Depends(require_manager_or_admin)
):
    return {"message": "Manager access granted"}
```

## 初始化管理员账户

首次部署时，运行以下命令创建管理员账户:

```bash
cd /mnt/e/agent/AdminAgent/backend
python -m app.scripts.create_admin
```

默认管理员凭据:
- 用户名: `admin`
- 密码: `admin123`
- 角色: `sys_admin`

⚠️ **重要**: 首次登录后请立即修改密码!

## 安全配置

### JWT 配置（在 .env 文件中）

```env
# JWT 密钥（生产环境必须使用强随机密钥）
JWT_SECRET_KEY=your-secret-key-change-in-production

# JWT 算法
JWT_ALGORITHM=HS256

# Token 过期时间（分钟）
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 生成安全的 JWT 密钥

```bash
# 使用 openssl 生成随机密钥
openssl rand -hex 32
```

## 权限矩阵

| 功能 | 员工 | 行政专员 | 部门主管 | 系统管理员 |
|------|------|---------|---------|----------|
| 提交工单 | ✓ | ✓ | ✓ | ✓ |
| 查看自己的工单 | ✓ | ✓ | ✓ | ✓ |
| 查看本部门工单 | ✗ | ✗ | ✓ | ✓ |
| 查看所有工单 | ✗ | ✓ | ✗ | ✓ |
| 接单/处理工单 | ✗ | ✓ | ✗ | ✓ |
| 审批工单 | ✗ | ✗ | ✓ | ✓ |
| 资产管理 | ✗ | ✓ | ✗ | ✓ |
| 系统配置 | ✗ | ✗ | ✗ | ✓ |
| 数据看板 | ✗ | ✓ | ✓ | ✓ |

## 测试

### 使用 curl 测试

```bash
# 1. 注册用户
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "password": "test123",
    "full_name": "测试用户",
    "department": "测试部"
  }'

# 2. 登录获取 token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "password": "test123"
  }'

# 3. 使用 token 访问受保护路由
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your_access_token>"
```

## 后续扩展

- [ ] Refresh Token 机制
- [ ] Token 黑名单（Redis）
- [ ] 登录日志记录
- [ ] 密码重置功能
- [ ] 多因素认证（MFA）
- [ ] OAuth2 第三方登录

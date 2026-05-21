# API Schemas Documentation

本目录包含所有API的请求和响应数据模型（Pydantic Schemas）。

## 概述

Schemas用于：
- **数据验证**：自动验证API请求数据
- **序列化**：将数据库模型转换为JSON响应
- **API文档**：自动生成OpenAPI/Swagger文档
- **类型安全**：提供IDE自动补全和类型检查

## Schema文件结构

```
schemas/
├── __init__.py           # 导出所有Schema
├── ticket.py             # 工单相关Schema
├── ticket_schema.py      # 工单扩展Schema（AI解析等）
├── asset.py              # 资产相关Schema
├── task.py               # 任务相关Schema
└── approval.py           # 审批相关Schema
```

## Ticket Schemas (工单)

### 基础操作

**TicketCreate** - 创建工单
```python
{
    "original_text": "会议室投影仪坏了",
    "attachments": ["https://example.com/image.jpg"],
    "title": "会议室投影仪报修",
    "ticket_type": "repair",
    "urgency_level": 4,
    "estimated_cost": 500.0
}
```

**TicketUpdate** - 更新工单
```python
{
    "title": "更新后的标题",
    "urgency_level": 5,
    "actual_cost": 450.0
}
```

**TicketResponse** - 工单响应
```python
{
    "id": 1,
    "creator_id": 1,
    "title": "会议室投影仪报修",
    "ticket_type": "repair",
    "approval_status": "pending_manager",
    "processing_status": "pending",
    "created_at": "2024-05-19T10:00:00Z",
    ...
}
```

### 特殊操作

**TicketAIParse** - AI解析工单
```python
{
    "original_text": "需要采购10台笔记本电脑",
    "attachments": []
}
```

**TicketApproval** - 审批工单
```python
{
    "approval_status": "approved",
    "notes": "同意采购"
}
```

**TicketAssign** - 分配工单
```python
{
    "admin_id": 2
}
```

**TicketClose** - 关闭工单
```python
{
    "actual_cost": 450.0
}
```

## Asset Schemas (资产)

### 基础操作

**AssetCreate** - 创建资产
```python
{
    "asset_code": "IT-2024-001",
    "asset_name": "联想ThinkPad笔记本",
    "category": "it_equipment",
    "status": "idle",
    "current_stock": 1,
    "unit_price": 6500.0,
    "brand": "联想",
    "model": "ThinkPad X1 Carbon",
    "location": "3楼技术部"
}
```

**AssetUpdate** - 更新资产
```python
{
    "status": "in_use",
    "owner_id": 1,
    "location": "4楼会议室"
}
```

**AssetResponse** - 资产响应
```python
{
    "id": 1,
    "asset_code": "IT-2024-001",
    "asset_name": "联想ThinkPad笔记本",
    "category": "it_equipment",
    "status": "in_use",
    "owner_id": 1,
    "current_stock": 1,
    "created_at": "2024-05-19T10:00:00Z",
    ...
}
```

### 特殊操作

**AssetStockUpdate** - 更新库存
```python
{
    "quantity_change": -5,  // 减少5个
    "notes": "发放给技术部"
}
```

**AssetAssign** - 分配资产
```python
{
    "user_id": 1
}
```

**AssetStatistics** - 资产统计
```python
{
    "total_count": 100,
    "idle_count": 20,
    "in_use_count": 70,
    "under_repair_count": 5,
    "scrapped_count": 5,
    "total_value": 500000.0,
    "total_stock": 100
}
```

## Task Schemas (任务)

### 基础操作

**TaskCreate** - 创建任务
```python
{
    "ticket_id": 1,
    "task_name": "联系供应商维修投影仪",
    "description": "联系华强北电子城的维修商",
    "assignee_id": 2,
    "deadline": "2024-05-25T18:00:00Z",
    "budget": 500.0,
    "supplier_name": "华强北电子维修中心",
    "supplier_contact": "李师傅",
    "supplier_phone": "13900139000"
}
```

**TaskUpdate** - 更新任务
```python
{
    "status": "in_progress",
    "progress_percentage": 60,
    "notes": "已联系供应商，预计明天上门"
}
```

**TaskResponse** - 任务响应
```python
{
    "id": 1,
    "ticket_id": 1,
    "task_name": "联系供应商维修投影仪",
    "assignee_id": 2,
    "status": "in_progress",
    "progress_percentage": 60,
    "deadline": "2024-05-25T18:00:00Z",
    "created_at": "2024-05-19T10:00:00Z",
    ...
}
```

### 特殊操作

**TaskStart** - 开始任务
```python
{
    "notes": "开始处理"
}
```

**TaskComplete** - 完成任务
```python
{
    "actual_cost": 450.0,
    "notes": "维修完成"
}
```

**TaskProgressUpdate** - 更新进度
```python
{
    "progress_percentage": 80,
    "notes": "供应商已到场，正在维修"
}
```

**TaskCancel** - 取消任务
```python
{
    "reason": "工单已取消"
}
```

**TaskKanbanResponse** - 看板视图
```python
{
    "todo": [...],
    "in_progress": [...],
    "completed": [...],
    "cancelled": [...]
}
```

**TaskStatistics** - 任务统计
```python
{
    "total_tasks": 50,
    "status_counts": {
        "todo": 10,
        "in_progress": 15,
        "completed": 20,
        "cancelled": 5
    },
    "completion_rate": 40.0,
    "avg_completion_time_hours": 24.5,
    "overdue_count": 3,
    "total_budget": 50000.0,
    "total_actual_cost": 45000.0
}
```

## 列表响应格式

所有列表API都使用统一的分页响应格式：

```python
{
    "total": 100,        // 总记录数
    "items": [...],      // 当前页数据
    "skip": 0,           // 跳过的记录数
    "limit": 20          // 每页记录数
}
```

## 数据验证规则

### 字符串长度
- 标题/名称：1-200字符
- 编号：1-50字符
- 描述/备注：无限制
- 联系方式：最多20字符

### 数值范围
- 紧急程度：1-5
- 进度百分比：0-100
- 金额：>= 0
- 库存：>= 0

### 枚举类型
- **TicketType**: procurement, repair, requisition, consultation
- **ApprovalStatus**: no_approval_needed, pending_manager, pending_finance, approved, rejected
- **ProcessingStatus**: pending, in_progress, completed
- **AssetCategory**: it_equipment, office_furniture, consumables
- **AssetStatus**: idle, in_use, under_repair, scrapped
- **TaskStatus**: todo, in_progress, completed, cancelled

## 使用示例

### 在API路由中使用

```python
from fastapi import APIRouter, Depends
from app.schemas import TicketCreate, TicketResponse

router = APIRouter()

@router.post("/tickets", response_model=TicketResponse)
def create_ticket(ticket_data: TicketCreate):
    # ticket_data 已自动验证
    # 返回值会自动序列化为 TicketResponse
    ...
```

### 在Service层使用

```python
from app.schemas import AssetUpdate

def update_asset(asset_id: int, update_data: AssetUpdate):
    # update_data.dict(exclude_unset=True) 只包含提供的字段
    update_dict = update_data.dict(exclude_unset=True)
    ...
```

## 自动生成的API文档

所有Schema会自动生成OpenAPI文档，访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 最佳实践

1. **使用明确的Schema名称**
   - Create: 创建操作
   - Update: 更新操作（部分字段可选）
   - Response: 响应数据

2. **添加描述和示例**
   ```python
   Field(..., description="字段说明", example="示例值")
   ```

3. **使用验证器**
   ```python
   @validator('field_name')
   def validate_field(cls, v):
       if not valid:
           raise ValueError('错误信息')
       return v
   ```

4. **继承基础Schema**
   ```python
   class Base(BaseModel):
       common_field: str

   class Create(Base):
       pass  # 继承所有字段

   class Update(BaseModel):
       common_field: Optional[str] = None  # 可选更新
   ```

## 相关文档

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)

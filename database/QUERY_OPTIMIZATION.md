# 查询性能优化策略

## 1. 查询优化原则

### 1.1 优化目标

- **响应时间**：列表查询 < 50ms，复杂查询 < 200ms
- **吞吐量**：支持1000+ QPS
- **资源利用**：CPU < 60%，内存命中率 > 95%
- **可扩展性**：支持100万+数据量

### 1.2 优化层次

```
应用层优化（ORM查询）
    ↓
数据库层优化（索引、查询计划）
    ↓
架构层优化（缓存、读写分离）
    ↓
硬件层优化（SSD、内存）
```

## 2. SQLModel查询优化

### 2.1 避免N+1查询问题

**❌ 错误示例：**
```python
# N+1问题：查询100个工单会执行101次SQL
tickets = session.exec(select(Ticket).limit(100)).all()
for ticket in tickets:
    creator_name = ticket.creator.full_name  # 每次触发一次查询
```

**✅ 正确示例：**
```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# 使用selectinload预加载关联数据（2次SQL）
statement = (
    select(Ticket)
    .options(selectinload(Ticket.creator))
    .limit(100)
)
tickets = session.exec(statement).all()
for ticket in tickets:
    creator_name = ticket.creator.full_name  # 无额外查询
```

**性能对比：**
- N+1查询：101次SQL，耗时 ~500ms
- selectinload：2次SQL，耗时 ~15ms
- **性能提升：33倍**

### 2.2 使用joinedload优化

```python
from sqlalchemy.orm import joinedload

# 一次SQL完成（LEFT JOIN）
statement = (
    select(Ticket)
    .options(joinedload(Ticket.creator))
    .options(joinedload(Ticket.related_asset))
    .where(Ticket.processing_status == ProcessingStatus.PENDING)
    .limit(20)
)
tickets = session.exec(statement).all()
```

**选择建议：**
- `selectinload`：一对多关系（避免笛卡尔积）
- `joinedload`：一对一/多对一关系

### 2.3 仅查询需要的字段

**❌ 错误示例：**
```python
# 查询所有字段（包括大字段）
tickets = session.exec(select(Ticket)).all()
```

**✅ 正确示例：**
```python
# 仅查询列表需要的字段
statement = select(
    Ticket.id,
    Ticket.title,
    Ticket.ticket_type,
    Ticket.urgency_level,
    Ticket.created_at
).where(Ticket.processing_status == ProcessingStatus.PENDING)

results = session.exec(statement).all()
```

**性能提升：**
- 减少网络传输：数据量减少60%
- 提升缓存命中：更多数据可缓存在内存

### 2.4 分页查询优化

**❌ 错误示例（深分页）：**
```python
# 查询第1000页，需要扫描20000条数据
tickets = session.exec(
    select(Ticket)
    .order_by(Ticket.created_at.desc())
    .offset(20000)
    .limit(20)
).all()
```

**✅ 正确示例（游标分页）：**
```python
# 使用上一页最后一条记录的ID作为游标
statement = (
    select(Ticket)
    .where(Ticket.id < last_id)  # 游标
    .order_by(Ticket.id.desc())
    .limit(20)
)
tickets = session.exec(statement).all()
```

**性能对比：**
- OFFSET分页：扫描20000条，耗时 ~300ms
- 游标分页：扫描20条，耗时 ~5ms
- **性能提升：60倍**

### 2.5 批量操作优化

**❌ 错误示例：**
```python
# 逐条插入（100次SQL）
for i in range(100):
    asset = Asset(asset_code=f"IT-{i}", asset_name=f"设备{i}")
    session.add(asset)
    session.commit()  # 每次提交触发一次IO
```

**✅ 正确示例：**
```python
# 批量插入（1次SQL）
assets = [
    Asset(asset_code=f"IT-{i}", asset_name=f"设备{i}")
    for i in range(100)
]
session.add_all(assets)
session.commit()
```

**性能提升：100倍**

## 3. 复杂查询优化

### 3.1 工单统计查询

**需求：** 按工单类型统计数量和平均处理时长

```python
from sqlalchemy import func, case
from datetime import datetime, timedelta

# 优化后的统计查询
statement = (
    select(
        Ticket.ticket_type,
        func.count(Ticket.id).label('total_count'),
        func.avg(
            func.extract('epoch', Ticket.closed_at - Ticket.created_at)
        ).label('avg_duration_seconds'),
        func.count(
            case((Ticket.urgency_level >= 4, 1))
        ).label('urgent_count')
    )
    .where(Ticket.created_at >= datetime.utcnow() - timedelta(days=30))
    .group_by(Ticket.ticket_type)
)

results = session.exec(statement).all()
```

**优化要点：**
- 使用数据库聚合函数（避免Python循环）
- 添加时间范围过滤（利用索引）
- 使用`case`表达式实现条件统计

### 3.2 部门工单查询（权限过滤）

```python
from sqlalchemy import exists

# 主管查看本部门工单
def get_department_tickets(user: User, session: Session):
    if user.role == UserRole.MANAGER:
        # 子查询：本部门所有用户ID
        dept_users_subq = (
            select(User.id)
            .where(User.department == user.department)
            .where(User.is_active == True)
        ).subquery()

        statement = (
            select(Ticket)
            .where(Ticket.creator_id.in_(dept_users_subq))
            .order_by(Ticket.created_at.desc())
        )
    elif user.role == UserRole.ADMIN:
        # 行政人员查看所有工单
        statement = select(Ticket).order_by(Ticket.created_at.desc())
    else:
        # 员工仅查看自己的工单
        statement = (
            select(Ticket)
            .where(Ticket.creator_id == user.id)
            .order_by(Ticket.created_at.desc())
        )

    return session.exec(statement).all()
```

### 3.3 资产库存预警查询

```python
# 查询库存低于阈值的耗材
statement = (
    select(Asset)
    .where(Asset.category == AssetCategory.CONSUMABLES)
    .where(Asset.current_stock < 10)
    .order_by(Asset.current_stock.asc())
)

low_stock_assets = session.exec(statement).all()
```

**索引支持：** `idx_assets_stock_alert`

## 4. 缓存策略

### 4.1 Redis缓存设计

```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_query(key_prefix: str, ttl: int = 300):
    """查询结果缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"

            # 尝试从缓存读取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # 执行查询
            result = await func(*args, **kwargs)

            # 写入缓存
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str)
            )
            return result
        return wrapper
    return decorator

# 使用示例
@cache_query(key_prefix="ticket_stats", ttl=600)
async def get_ticket_statistics(date_range: str):
    # 执行统计查询
    pass
```

### 4.2 缓存失效策略

```python
class TicketService:
    def create_ticket(self, ticket_data: dict, session: Session):
        # 创建工单
        ticket = Ticket(**ticket_data)
        session.add(ticket)
        session.commit()

        # 清除相关缓存
        redis_client.delete(f"ticket_stats:*")
        redis_client.delete(f"user_tickets:{ticket.creator_id}")

        return ticket
```

### 4.3 缓存预热

```python
async def warmup_cache():
    """系统启动时预热热点数据"""
    # 缓存活跃用户列表
    active_users = session.exec(
        select(User).where(User.is_active == True)
    ).all()
    redis_client.setex(
        "active_users",
        3600,
        json.dumps([u.dict() for u in active_users], default=str)
    )

    # 缓存系统配置
    configs = session.exec(select(SysConfig)).all()
    for config in configs:
        redis_client.setex(
            f"config:{config.key}",
            300,
            config.value
        )
```

## 5. 数据库连接池优化

### 5.1 SQLAlchemy连接池配置

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,              # 常驻连接数
    max_overflow=10,           # 最大溢出连接数
    pool_timeout=30,           # 获取连接超时时间
    pool_recycle=3600,         # 连接回收时间（避免MySQL 8小时超时）
    pool_pre_ping=True,        # 连接前检测可用性
    echo=False,                # 生产环境关闭SQL日志
    echo_pool=False,
)
```

### 5.2 连接池监控

```python
def get_pool_status():
    """监控连接池状态"""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total": pool.size() + pool.overflow()
    }
```

## 6. 慢查询监控

### 6.1 PostgreSQL慢查询日志

```sql
-- 配置慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 100;  -- 记录>100ms的查询
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';
SELECT pg_reload_conf();

-- 查看慢查询统计
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### 6.2 应用层监控

```python
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def monitor_query(threshold_ms: int = 100):
    """查询性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start) * 1000

            if duration_ms > threshold_ms:
                logger.warning(
                    f"Slow query detected: {func.__name__} "
                    f"took {duration_ms:.2f}ms"
                )
            return result
        return wrapper
    return decorator

# 使用示例
@monitor_query(threshold_ms=50)
def get_pending_tickets(session: Session):
    return session.exec(
        select(Ticket).where(Ticket.processing_status == ProcessingStatus.PENDING)
    ).all()
```

## 7. 查询优化检查清单

### 7.1 开发阶段

- [ ] 使用`selectinload`/`joinedload`避免N+1查询
- [ ] 仅查询需要的字段（避免`SELECT *`）
- [ ] 添加合适的WHERE条件（利用索引）
- [ ] 使用游标分页（避免深分页）
- [ ] 批量操作使用`add_all`（避免循环提交）

### 7.2 测试阶段

- [ ] 使用`EXPLAIN ANALYZE`分析查询计划
- [ ] 验证索引是否生效（Index Scan）
- [ ] 测试大数据量场景（10万+记录）
- [ ] 压测并发查询（100+ QPS）

### 7.3 生产阶段

- [ ] 监控慢查询日志
- [ ] 定期分析索引使用情况
- [ ] 监控连接池状态
- [ ] 定期VACUUM和ANALYZE

## 8. 性能优化案例

### 案例1：工单列表查询优化

**优化前：**
```python
tickets = session.exec(select(Ticket)).all()  # 450ms
```

**优化后：**
```python
statement = (
    select(
        Ticket.id,
        Ticket.title,
        Ticket.ticket_type,
        Ticket.urgency_level,
        Ticket.created_at
    )
    .where(Ticket.processing_status != ProcessingStatus.COMPLETED)
    .order_by(Ticket.created_at.desc())
    .limit(20)
)
tickets = session.exec(statement).all()  # 8ms
```

**优化效果：56倍提升**

### 案例2：统计查询优化

**优化前（Python循环）：**
```python
tickets = session.exec(select(Ticket)).all()
stats = {}
for ticket in tickets:
    stats[ticket.ticket_type] = stats.get(ticket.ticket_type, 0) + 1
# 耗时：2000ms
```

**优化后（数据库聚合）：**
```python
statement = (
    select(Ticket.ticket_type, func.count(Ticket.id))
    .group_by(Ticket.ticket_type)
)
stats = dict(session.exec(statement).all())
# 耗时：15ms
```

**优化效果：133倍提升**

## 9. 总结

**查询优化核心原则：**

1. **减少查询次数**：预加载关联数据，批量操作
2. **减少数据量**：仅查询需要的字段，添加过滤条件
3. **利用索引**：WHERE/ORDER BY字段建立索引
4. **使用缓存**：热点数据缓存到Redis
5. **监控优化**：持续监控慢查询，及时优化

**预期性能指标：**
- 列表查询：< 50ms
- 详情查询：< 20ms
- 统计查询：< 200ms
- 并发支持：1000+ QPS
- 缓存命中率：> 80%

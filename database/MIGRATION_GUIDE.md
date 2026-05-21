# 数据库迁移脚本设计

## 1. Alembic配置

### 1.1 初始化Alembic

```bash
cd /mnt/e/agent/AdminAgent/backend
pip install alembic
alembic init alembic
```

### 1.2 配置文件 `alembic.ini`

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://admin_user:password@localhost:5432/admin_agent_db

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 100

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### 1.3 环境配置 `alembic/env.py`

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.models import *  # 导入所有模型
from sqlmodel import SQLModel

config = context.config

# 从环境变量读取数据库URL
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """离线模式迁移（生成SQL文件）"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """在线模式迁移（直接执行）"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## 2. 初始化迁移脚本

### 2.1 创建初始迁移

```bash
# 生成初始迁移脚本
alembic revision --autogenerate -m "Initial database schema"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 2.2 初始迁移脚本示例

**文件：** `alembic/versions/001_initial_schema.py`

```python
"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-05-19 17:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 创建枚举类型
    user_role_enum = postgresql.ENUM(
        'employee', 'admin', 'manager', 'system_admin',
        name='userrole',
        create_type=False
    )
    user_role_enum.create(op.get_bind(), checkfirst=True)

    asset_category_enum = postgresql.ENUM(
        'it_equipment', 'office_furniture', 'consumables',
        name='assetcategory',
        create_type=False
    )
    asset_category_enum.create(op.get_bind(), checkfirst=True)

    asset_status_enum = postgresql.ENUM(
        'idle', 'in_use', 'under_repair', 'scrapped',
        name='assetstatus',
        create_type=False
    )
    asset_status_enum.create(op.get_bind(), checkfirst=True)

    ticket_type_enum = postgresql.ENUM(
        'procurement', 'repair', 'requisition', 'consultation',
        name='tickettype',
        create_type=False
    )
    ticket_type_enum.create(op.get_bind(), checkfirst=True)

    approval_status_enum = postgresql.ENUM(
        'no_approval_needed', 'pending_manager', 'pending_finance', 'approved', 'rejected',
        name='approvalstatus',
        create_type=False
    )
    approval_status_enum.create(op.get_bind(), checkfirst=True)

    processing_status_enum = postgresql.ENUM(
        'pending', 'in_progress', 'completed',
        name='processingstatus',
        create_type=False
    )
    processing_status_enum.create(op.get_bind(), checkfirst=True)

    task_status_enum = postgresql.ENUM(
        'todo', 'in_progress', 'completed', 'cancelled',
        name='taskstatus',
        create_type=False
    )
    task_status_enum.create(op.get_bind(), checkfirst=True)

    # 创建users表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', user_role_enum, nullable=False, server_default='employee'),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index('idx_users_username', 'users', ['username'], unique=True)
    op.create_index('idx_users_dept_role', 'users', ['department', 'role'], postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_users_email', 'users', ['email'], postgresql_where=sa.text('email IS NOT NULL'))

    # 创建assets表
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_code', sa.String(length=50), nullable=False),
        sa.Column('asset_name', sa.String(length=200), nullable=False),
        sa.Column('category', asset_category_enum, nullable=False),
        sa.Column('status', asset_status_enum, nullable=False, server_default='idle'),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('current_stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('unit_price', sa.Float(), nullable=True),
        sa.Column('purchase_date', sa.DateTime(), nullable=True),
        sa.Column('warranty_until', sa.DateTime(), nullable=True),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('specifications', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('supplier', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_code')
    )
    op.create_index('idx_assets_code', 'assets', ['asset_code'], unique=True)
    op.create_index('idx_assets_status', 'assets', ['status', 'category'])
    op.create_index('idx_assets_owner', 'assets', ['owner_id'], postgresql_where=sa.text('owner_id IS NOT NULL'))

    # 创建tickets表
    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('attachments', sa.Text(), nullable=True),
        sa.Column('ticket_type', ticket_type_enum, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('urgency_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('related_asset_id', sa.Integer(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('actual_cost', sa.Float(), nullable=True),
        sa.Column('approval_status', approval_status_enum, nullable=False, server_default='no_approval_needed'),
        sa.Column('approved_by_manager_id', sa.Integer(), nullable=True),
        sa.Column('approved_by_finance_id', sa.Integer(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('processing_status', processing_status_enum, nullable=False, server_default='pending'),
        sa.Column('assigned_admin_id', sa.Integer(), nullable=True),
        sa.Column('ai_confidence_score', sa.Float(), nullable=True),
        sa.Column('ai_parsed_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_asset_id'], ['assets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_admin_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tickets_creator', 'tickets', ['creator_id'])
    op.create_index('idx_tickets_status_composite', 'tickets', 
                    ['processing_status', 'approval_status', sa.text('created_at DESC')],
                    postgresql_where=sa.text("processing_status != 'completed'"))
    op.create_index('idx_tickets_created_at', 'tickets', [sa.text('created_at DESC')])

    # 创建tasks表
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('task_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', task_status_enum, nullable=False, server_default='todo'),
        sa.Column('assignee_id', sa.Integer(), nullable=False),
        sa.Column('supplier_name', sa.String(length=200), nullable=True),
        sa.Column('supplier_contact', sa.String(length=100), nullable=True),
        sa.Column('supplier_phone', sa.String(length=20), nullable=True),
        sa.Column('external_contact', sa.String(length=200), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('budget', sa.Float(), nullable=True),
        sa.Column('actual_cost', sa.Float(), nullable=True),
        sa.Column('progress_percentage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tasks_ticket', 'tasks', ['ticket_id'])
    op.create_index('idx_tasks_assignee', 'tasks', ['assignee_id'])
    op.create_index('idx_tasks_kanban', 'tasks', ['status', 'assignee_id', 'deadline'],
                    postgresql_where=sa.text("status IN ('todo', 'in_progress')"))

    # 创建触发器：自动更新updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    for table in ['users', 'assets', 'tickets', 'tasks']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)

def downgrade() -> None:
    # 删除触发器
    for table in ['users', 'assets', 'tickets', 'tasks']:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # 删除表
    op.drop_table('tasks')
    op.drop_table('tickets')
    op.drop_table('assets')
    op.drop_table('users')

    # 删除枚举类型
    sa.Enum(name='taskstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='processingstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='approvalstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='tickettype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='assetstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='assetcategory').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
```

## 3. 常用迁移命令

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history --verbose

# 生成新迁移
alembic revision --autogenerate -m "Add knowledge_base table"

# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade 002

# 回滚一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade 001

# 生成SQL而不执行
alembic upgrade head --sql > migration.sql

# 标记当前数据库版本（不执行迁移）
alembic stamp head
```

## 4. 数据迁移最佳实践

### 4.1 安全迁移流程

```bash
# 1. 备份数据库
pg_dump -U admin_user -d admin_agent_db -F c -f backup_$(date +%Y%m%d_%H%M%S).dump

# 2. 在测试环境验证迁移
alembic upgrade head --sql > migration.sql
psql -U admin_user -d admin_agent_db_test -f migration.sql

# 3. 生产环境执行
alembic upgrade head

# 4. 验证数据完整性
psql -U admin_user -d admin_agent_db -c "SELECT COUNT(*) FROM users;"
```

### 4.2 零停机迁移策略

```python
# 示例：添加新列（分两步）

# 步骤1：添加可空列
def upgrade():
    op.add_column('tickets', sa.Column('priority', sa.String(20), nullable=True))

# 步骤2（下一个版本）：填充数据后设为NOT NULL
def upgrade():
    op.execute("UPDATE tickets SET priority = 'normal' WHERE priority IS NULL")
    op.alter_column('tickets', 'priority', nullable=False)
```

## 5. 迁移脚本模板

### 5.1 添加表

```python
def upgrade():
    op.create_table(
        'knowledge_base',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_kb_category', 'knowledge_base', ['category'])

def downgrade():
    op.drop_table('knowledge_base')
```

### 5.2 修改列

```python
def upgrade():
    op.alter_column('tickets', 'urgency_level',
                    existing_type=sa.Integer(),
                    type_=sa.SmallInteger(),
                    existing_nullable=False)

def downgrade():
    op.alter_column('tickets', 'urgency_level',
                    existing_type=sa.SmallInteger(),
                    type_=sa.Integer(),
                    existing_nullable=False)
```

### 5.3 数据迁移

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

def upgrade():
    # 定义临时表结构
    tickets_table = table('tickets',
        column('id', sa.Integer),
        column('urgency_level', sa.Integer),
        column('priority', sa.String)
    )

    # 数据转换
    op.execute(
        tickets_table.update()
        .where(tickets_table.c.urgency_level >= 4)
        .values(priority='high')
    )
    op.execute(
        tickets_table.update()
        .where(tickets_table.c.urgency_level < 4)
        .values(priority='normal')
    )

def downgrade():
    pass
```

## 6. 总结

本迁移方案提供：

1. **版本控制**：使用Alembic管理数据库schema变更
2. **自动化**：通过`--autogenerate`自动检测模型变更
3. **可回滚**：每个迁移都包含upgrade和downgrade逻辑
4. **安全性**：支持离线生成SQL、分步迁移、零停机部署
5. **可追溯**：完整的迁移历史记录

**注意事项：**
- 生产环境迁移前务必备份
- 大表修改使用`CONCURRENTLY`选项
- 复杂迁移分多个版本执行
- 定期清理过期的迁移脚本

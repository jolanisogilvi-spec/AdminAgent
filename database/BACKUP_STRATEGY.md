# 数据库备份与恢复策略

## 1. 备份策略概述

### 1.1 备份目标

- **RPO (Recovery Point Objective)**：数据恢复点目标 ≤ 1小时
- **RTO (Recovery Time Objective)**：恢复时间目标 ≤ 30分钟
- **数据完整性**：确保备份数据可用且一致
- **存储成本**：平衡备份频率与存储成本

### 1.2 备份类型

| 备份类型 | 频率 | 保留期 | 恢复速度 | 存储空间 |
|---------|------|--------|---------|--------|
| 全量备份 | 每日 | 30天 | 快 | 大 |
| 增量备份 | 每小时 | 7天 | 中 | 小 |
| WAL归档 | 实时 | 7天 | 快 | 中 |
| 逻辑备份 | 每周 | 90天 | 慢 | 中 |

## 2. 物理备份（推荐）

### 2.1 使用pg_basebackup

**优势：**
- 备份速度快（直接复制数据文件）
- 支持增量恢复（结合WAL）
- 可用于搭建从库

**配置步骤：**

#### 步骤1：配置WAL归档

编辑 `postgresql.conf`：
```ini
# WAL配置
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /mnt/backup/wal_archive/%f && cp %p /mnt/backup/wal_archive/%f'
archive_timeout = 300  # 5分钟强制切换WAL

# 复制配置
max_wal_senders = 3
wal_keep_size = 1GB
```

编辑 `pg_hba.conf`：
```
# 允许复制连接
host    replication     backup_user     127.0.0.1/32            md5
```

重启PostgreSQL：
```bash
sudo systemctl restart postgresql
```

#### 步骤2：创建备份用户

```sql
CREATE ROLE backup_user WITH REPLICATION LOGIN PASSWORD 'secure_password';
```

#### 步骤3：执行全量备份

```bash
#!/bin/bash
# 文件：/opt/scripts/pg_full_backup.sh

BACKUP_DIR="/mnt/backup/pg_basebackup"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/backup_${DATE}"

# 创建备份目录
mkdir -p "${BACKUP_PATH}"

# 执行备份
pg_basebackup \
    -h localhost \
    -U backup_user \
    -D "${BACKUP_PATH}" \
    -Ft \
    -z \
    -P \
    -X stream

if [ $? -eq 0 ]; then
    echo "[$(date)] Backup successful: ${BACKUP_PATH}" >> /var/log/pg_backup.log

    # 删除30天前的备份
    find "${BACKUP_DIR}" -type d -name "backup_*" -mtime +30 -exec rm -rf {} \;
else
    echo "[$(date)] Backup failed!" >> /var/log/pg_backup.log
    exit 1
fi
```

**参数说明：**
- `-Ft`: tar格式压缩
- `-z`: gzip压缩
- `-P`: 显示进度
- `-X stream`: 流式传输WAL

### 2.2 WAL归档备份

**归档脚本：**
```bash
#!/bin/bash
# 文件：/opt/scripts/archive_wal.sh

WAL_FILE=$1
ARCHIVE_DIR="/mnt/backup/wal_archive"

# 复制WAL文件
cp "${WAL_FILE}" "${ARCHIVE_DIR}/"

if [ $? -eq 0 ]; then
    # 上传到云存储（可选）
    # aws s3 cp "${ARCHIVE_DIR}/$(basename ${WAL_FILE})" s3://my-bucket/wal_archive/

    # 删除7天前的WAL
    find "${ARCHIVE_DIR}" -type f -mtime +7 -delete

    exit 0
else
    exit 1
fi
```

更新 `postgresql.conf`：
```ini
archive_command = '/opt/scripts/archive_wal.sh %p'
```

### 2.3 自动化备份（Cron）

```bash
# 编辑crontab
crontab -e

# 添加定时任务
# 每天凌晨2点执行全量备份
0 2 * * * /opt/scripts/pg_full_backup.sh

# 每小时执行增量备份（通过WAL归档自动完成）
# 无需额外配置

# 每周日凌晨3点执行逻辑备份
0 3 * * 0 /opt/scripts/pg_dump_backup.sh
```

## 3. 逻辑备份

### 3.1 使用pg_dump

**全库备份：**
```bash
#!/bin/bash
# 文件：/opt/scripts/pg_dump_backup.sh

BACKUP_DIR="/mnt/backup/pg_dump"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="admin_agent_db"

# 自定义格式备份（推荐）
pg_dump \
    -U postgres \
    -d "${DB_NAME}" \
    -F c \
    -b \
    -v \
    -f "${BACKUP_DIR}/${DB_NAME}_${DATE}.dump"

if [ $? -eq 0 ]; then
    echo "[$(date)] Logical backup successful" >> /var/log/pg_backup.log

    # 压缩备份文件
    gzip "${BACKUP_DIR}/${DB_NAME}_${DATE}.dump"

    # 删除90天前的备份
    find "${BACKUP_DIR}" -type f -name "*.dump.gz" -mtime +90 -delete
else
    echo "[$(date)] Logical backup failed!" >> /var/log/pg_backup.log
    exit 1
fi
```

**参数说明：**
- `-F c`: 自定义格式（支持并行恢复）
- `-b`: 包含大对象
- `-v`: 详细输出

**仅备份schema：**
```bash
pg_dump -U postgres -d admin_agent_db -s -f schema_only.sql
```

**仅备份数据：**
```bash
pg_dump -U postgres -d admin_agent_db -a -f data_only.sql
```

**备份单表：**
```bash
pg_dump -U postgres -d admin_agent_db -t tickets -F c -f tickets_backup.dump
```

### 3.2 使用pg_dumpall

**备份所有数据库（包括角色）：**
```bash
pg_dumpall -U postgres -f /mnt/backup/all_databases_$(date +%Y%m%d).sql
```

## 4. 数据恢复

### 4.1 从物理备份恢复

**场景1：完全恢复（恢复到备份时间点）**

```bash
#!/bin/bash
# 停止PostgreSQL
sudo systemctl stop postgresql

# 清空数据目录
rm -rf /var/lib/postgresql/15/main/*

# 解压备份
tar -xzf /mnt/backup/pg_basebackup/backup_20240519/base.tar.gz -C /var/lib/postgresql/15/main/
tar -xzf /mnt/backup/pg_basebackup/backup_20240519/pg_wal.tar.gz -C /var/lib/postgresql/15/main/pg_wal/

# 修改权限
chown -R postgres:postgres /var/lib/postgresql/15/main/

# 启动PostgreSQL
sudo systemctl start postgresql
```

**场景2：PITR（Point-In-Time Recovery）**

创建 `recovery.conf`（PostgreSQL 12+使用 `postgresql.auto.conf`）：
```bash
# 文件：/var/lib/postgresql/15/main/recovery.signal
touch /var/lib/postgresql/15/main/recovery.signal
```

编辑 `postgresql.auto.conf`：
```ini
restore_command = 'cp /mnt/backup/wal_archive/%f %p'
recovery_target_time = '2024-05-19 14:30:00'
recovery_target_action = 'promote'
```

启动数据库：
```bash
sudo systemctl start postgresql
```

**恢复验证：**
```sql
-- 检查恢复时间点
SELECT pg_last_xact_replay_timestamp();

-- 检查数据完整性
SELECT COUNT(*) FROM tickets;
```

### 4.2 从逻辑备份恢复

**恢复整个数据库：**
```bash
# 删除现有数据库
dropdb -U postgres admin_agent_db

# 创建新数据库
createdb -U postgres admin_agent_db

# 恢复数据
pg_restore \
    -U postgres \
    -d admin_agent_db \
    -v \
    -j 4 \
    /mnt/backup/pg_dump/admin_agent_db_20240519.dump
```

**参数说明：**
- `-j 4`: 使用4个并行任务（加速恢复）
- `-v`: 详细输出

**恢复单表：**
```bash
pg_restore \
    -U postgres \
    -d admin_agent_db \
    -t tickets \
    /mnt/backup/pg_dump/admin_agent_db_20240519.dump
```

**仅恢复schema：**
```bash
pg_restore -U postgres -d admin_agent_db -s backup.dump
```

**仅恢复数据：**
```bash
pg_restore -U postgres -d admin_agent_db -a backup.dump
```

## 5. 云备份策略

### 5.1 上传到AWS S3

```bash
#!/bin/bash
# 文件：/opt/scripts/upload_to_s3.sh

BACKUP_FILE=$1
S3_BUCKET="s3://my-company-db-backups"

# 上传备份
aws s3 cp "${BACKUP_FILE}" "${S3_BUCKET}/postgresql/$(date +%Y/%m/%d)/"

if [ $? -eq 0 ]; then
    echo "[$(date)] Uploaded to S3: ${BACKUP_FILE}" >> /var/log/s3_upload.log

    # 删除本地备份（保留3天）
    find /mnt/backup/pg_dump -type f -mtime +3 -delete
else
    echo "[$(date)] S3 upload failed: ${BACKUP_FILE}" >> /var/log/s3_upload.log
    exit 1
fi
```

**集成到备份脚本：**
```bash
# 在pg_dump_backup.sh末尾添加
/opt/scripts/upload_to_s3.sh "${BACKUP_DIR}/${DB_NAME}_${DATE}.dump.gz"
```

### 5.2 使用pgBackRest（企业级方案）

**安装：**
```bash
sudo apt install pgbackrest
```

**配置：**
```ini
# 文件：/etc/pgbackrest/pgbackrest.conf
[global]
repo1-path=/mnt/backup/pgbackrest
repo1-retention-full=2
repo1-retention-diff=7
log-level-console=info
log-level-file=debug

[admin_agent_db]
pg1-path=/var/lib/postgresql/15/main
pg1-port=5432
pg1-user=postgres
```

**执行备份：**
```bash
# 全量备份
pgbackrest --stanza=admin_agent_db backup --type=full

# 差异备份
pgbackrest --stanza=admin_agent_db backup --type=diff

# 增量备份
pgbackrest --stanza=admin_agent_db backup --type=incr
```

**恢复：**
```bash
pgbackrest --stanza=admin_agent_db restore
```

## 6. 备份监控与告警

### 6.1 备份状态检查脚本

```bash
#!/bin/bash
# 文件：/opt/scripts/check_backup_status.sh

BACKUP_DIR="/mnt/backup/pg_basebackup"
MAX_AGE_HOURS=26  # 备份不能超过26小时

# 查找最新备份
LATEST_BACKUP=$(find "${BACKUP_DIR}" -type d -name "backup_*" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2)

if [ -z "${LATEST_BACKUP}" ]; then
    echo "ERROR: No backup found!"
    # 发送告警邮件
    echo "No PostgreSQL backup found in ${BACKUP_DIR}" | mail -s "[CRITICAL] DB Backup Missing" admin@company.com
    exit 1
fi

# 检查备份时间
BACKUP_AGE_HOURS=$(( ($(date +%s) - $(stat -c %Y "${LATEST_BACKUP}")) / 3600 ))

if [ ${BACKUP_AGE_HOURS} -gt ${MAX_AGE_HOURS} ]; then
    echo "WARNING: Latest backup is ${BACKUP_AGE_HOURS} hours old"
    echo "Latest PostgreSQL backup is ${BACKUP_AGE_HOURS} hours old (threshold: ${MAX_AGE_HOURS}h)" | \
        mail -s "[WARNING] DB Backup Outdated" admin@company.com
    exit 1
else
    echo "OK: Latest backup is ${BACKUP_AGE_HOURS} hours old"
    exit 0
fi
```

**添加到Cron：**
```bash
# 每小时检查备份状态
0 * * * * /opt/scripts/check_backup_status.sh
```

### 6.2 Prometheus监控指标

```python
# 文件：backend/app/monitoring/backup_metrics.py
from prometheus_client import Gauge
import os
import time

backup_age_seconds = Gauge(
    'postgresql_backup_age_seconds',
    'Age of the latest PostgreSQL backup in seconds'
)

backup_size_bytes = Gauge(
    'postgresql_backup_size_bytes',
    'Size of the latest PostgreSQL backup in bytes'
)

def update_backup_metrics():
    backup_dir = "/mnt/backup/pg_basebackup"
    latest_backup = max(
        [os.path.join(backup_dir, d) for d in os.listdir(backup_dir) if d.startswith("backup_")],
        key=os.path.getmtime,
        default=None
    )

    if latest_backup:
        age = time.time() - os.path.getmtime(latest_backup)
        size = sum(os.path.getsize(os.path.join(latest_backup, f)) for f in os.listdir(latest_backup))

        backup_age_seconds.set(age)
        backup_size_bytes.set(size)
```

## 7. 灾难恢复演练

### 7.1 演练计划

**频率：** 每季度一次

**步骤：**
1. 在测试环境执行完整恢复流程
2. 验证数据完整性（记录数、关键业务数据）
3. 测试应用连接性
4. 记录恢复时间（RTO）
5. 生成演练报告

### 7.2 演练脚本

```bash
#!/bin/bash
# 文件：/opt/scripts/disaster_recovery_drill.sh

TEST_DB="admin_agent_db_test"
BACKUP_FILE="/mnt/backup/pg_dump/admin_agent_db_latest.dump"

echo "[$(date)] Starting disaster recovery drill..."

# 1. 删除测试数据库
dropdb -U postgres "${TEST_DB}" 2>/dev/null

# 2. 创建测试数据库
createdb -U postgres "${TEST_DB}"

# 3. 记录开始时间
START_TIME=$(date +%s)

# 4. 恢复数据
pg_restore -U postgres -d "${TEST_DB}" -j 4 "${BACKUP_FILE}"

if [ $? -ne 0 ]; then
    echo "[$(date)] Recovery FAILED!"
    exit 1
fi

# 5. 计算恢复时间
END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))

echo "[$(date)] Recovery completed in ${RECOVERY_TIME} seconds"

# 6. 验证数据完整性
USER_COUNT=$(psql -U postgres -d "${TEST_DB}" -t -c "SELECT COUNT(*) FROM users;")
TICKET_COUNT=$(psql -U postgres -d "${TEST_DB}" -t -c "SELECT COUNT(*) FROM tickets;")

echo "Users: ${USER_COUNT}"
echo "Tickets: ${TICKET_COUNT}"

# 7. 生成报告
cat > /tmp/dr_drill_report.txt <<EOF
Disaster Recovery Drill Report
Date: $(date)
Recovery Time: ${RECOVERY_TIME} seconds
Data Validation:
  - Users: ${USER_COUNT}
  - Tickets: ${TICKET_COUNT}
Status: SUCCESS
EOF

cat /tmp/dr_drill_report.txt | mail -s "DR Drill Report" admin@company.com

echo "[$(date)] Drill completed successfully"
```

## 8. 备份最佳实践

### 8.1 3-2-1备份原则

- **3份副本**：生产数据 + 2份备份
- **2种介质**：本地磁盘 + 云存储
- **1份异地**：不同地理位置（防火灾/地震）

### 8.2 备份验证

```bash
# 定期验证备份可用性
pg_restore --list /mnt/backup/pg_dump/admin_agent_db_latest.dump > /dev/null

if [ $? -eq 0 ]; then
    echo "Backup file is valid"
else
    echo "Backup file is corrupted!"
    # 发送告警
fi
```

### 8.3 备份加密

```bash
# 使用GPG加密备份
pg_dump -U postgres -d admin_agent_db -F c | \
    gpg --encrypt --recipient admin@company.com > backup_encrypted.dump.gpg

# 解密恢复
gpg --decrypt backup_encrypted.dump.gpg | \
    pg_restore -U postgres -d admin_agent_db
```

## 9. 总结

**备份策略总结：**

| 备份类型 | 工具 | 频率 | 保留期 | 用途 |
|---------|------|------|--------|-----|
| 物理全量 | pg_basebackup | 每日 | 30天 | 完整恢复 |
| WAL归档 | archive_command | 实时 | 7天 | PITR |
| 逻辑备份 | pg_dump | 每周 | 90天 | 跨版本迁移 |
| 云备份 | AWS S3 | 每日 | 1年 | 异地容灾 |

**关键指标：**
- RPO：1小时（通过WAL归档）
- RTO：30分钟（物理备份恢复）
- 备份成功率：> 99%
- 恢复演练：每季度一次

**监控告警：**
- 备份失败立即告警
- 备份超过26小时告警
- 每月生成备份报告

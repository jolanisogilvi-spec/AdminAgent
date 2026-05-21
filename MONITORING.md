# 监控和日志系统文档

## 概述

本项目使用完整的监控和日志聚合系统,包括:

- **Prometheus**: 指标收集和存储
- **Grafana**: 可视化仪表板
- **Loki**: 日志聚合
- **Promtail**: 日志收集代理
- **AlertManager**: 告警管理
- **Node Exporter**: 系统指标导出

## 快速开始

### 1. 启动监控栈

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件,配置必要的参数
vim .env

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 2. 访问监控界面

- **Grafana**: http://localhost:3001
  - 默认用户名: `admin`
  - 默认密码: `admin123` (首次登录后会要求修改)

- **Prometheus**: http://localhost:9090
  - 查看指标和告警规则

- **AlertManager**: http://localhost:9093
  - 管理告警

## 监控指标

### 应用指标

#### HTTP 请求指标

- `http_requests_total`: HTTP 请求总数
  - Labels: `method`, `endpoint`, `status`
  
- `http_request_duration_seconds`: HTTP 请求持续时间
  - Labels: `method`, `endpoint`
  
- `http_requests_in_progress`: 当前进行中的 HTTP 请求数
  - Labels: `method`, `endpoint`

#### 数据库指标

- `db_connection_pool_size`: 数据库连接池大小
- `db_connection_pool_used`: 当前使用的数据库连接数

#### AI 服务指标

- `ai_service_requests_total`: AI 服务请求总数
  - Labels: `service`, `status`
  
- `ai_service_duration_seconds`: AI 服务请求持续时间
  - Labels: `service`

#### 业务指标

- `ticket_pending_count`: 待处理工单数
- `ticket_processing_count`: 处理中工单数
- `ticket_completed_total`: 已完成工单总数
  - Labels: `type`

### 系统指标

- CPU 使用率
- 内存使用率
- 磁盘使用率
- 网络 I/O
- 容器状态

## 告警规则

### 严重告警 (Critical)

1. **ServiceDown**: 服务下线超过 2 分钟
2. **HighErrorRate**: 5xx 错误率超过 5%
3. **DatabaseConnectionPoolExhausted**: 数据库连接池使用率超过 90%

### 警告告警 (Warning)

1. **HighCPUUsage**: CPU 使用率超过 80%
2. **HighMemoryUsage**: 内存使用率超过 85%
3. **DiskSpaceLow**: 磁盘剩余空间低于 15%
4. **HighAPILatency**: API 95 分位响应时间超过 1 秒
5. **RedisMemoryHigh**: Redis 内存使用率超过 90%
6. **ContainerRestartingFrequently**: 容器频繁重启
7. **AIServiceHighFailureRate**: AI 服务调用失败率超过 10%
8. **TicketBacklogHigh**: 待处理工单超过 50 个

## 日志系统

### 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 日志查询

在 Grafana 的 Explore 页面,使用 Loki 数据源:

```logql
# 查看所有后端日志
{container="admin-agent-backend"}

# 查看错误日志
{container="admin-agent-backend"} |= "ERROR"

# 查看特定时间范围的日志
{container="admin-agent-backend"} |= "ERROR" [5m]

# 按日志级别过滤
{container="admin-agent-backend"} | json | level="ERROR"

# 查看包含特定 trace_id 的日志
{container="admin-agent-backend"} | json | trace_id="abc123"
```

## 健康检查端点

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

响应示例:
```json
{
  "status": "healthy",
  "timestamp": "2024-05-19T10:00:00Z",
  "checks": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### 2. 就绪检查 (Readiness)

```bash
curl http://localhost:8000/health/ready
```

### 3. 存活检查 (Liveness)

```bash
curl http://localhost:8000/health/live
```

### 4. Prometheus 指标

```bash
curl http://localhost:8000/metrics
```

## Grafana 仪表板

### 预配置仪表板

1. **系统概览**: 显示整体系统健康状况
2. **应用性能**: API 响应时间、请求量、错误率
3. **数据库监控**: 连接池、查询性能
4. **业务指标**: 工单统计、AI 服务调用

### 创建自定义仪表板

1. 登录 Grafana
2. 点击 "Create" -> "Dashboard"
3. 添加面板,选择 Prometheus 或 Loki 数据源
4. 配置查询和可视化选项
5. 保存仪表板

## 告警配置

### 邮件告警

编辑 `monitoring/alertmanager/alertmanager.yml`:

```yaml
global:
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alertmanager@example.com'
  smtp_auth_username: 'alertmanager@example.com'
  smtp_auth_password: 'your-password'

receivers:
  - name: 'email'
    email_configs:
      - to: 'admin@example.com'
```

### Webhook 告警

告警会发送到后端 API:

```
POST http://backend:8000/api/v1/alerts/webhook
```

可以在后端实现自定义告警处理逻辑,如:
- 发送钉钉/企业微信通知
- 创建工单
- 触发自动修复流程

## 性能优化建议

### 1. 指标采集优化

- 调整 `scrape_interval` (默认 15s)
- 使用 `relabel_configs` 过滤不需要的指标
- 启用指标压缩

### 2. 日志优化

- 设置合理的日志保留期 (默认 7 天)
- 使用结构化日志 (JSON 格式)
- 避免记录敏感信息

### 3. 存储优化

- 定期清理旧数据
- 使用 SSD 存储
- 配置合适的保留策略

## 故障排查

### 1. Prometheus 无法抓取指标

```bash
# 检查目标状态
curl http://localhost:9090/api/v1/targets

# 检查服务是否暴露指标端点
curl http://backend:8000/metrics
```

### 2. Grafana 无法连接数据源

```bash
# 检查 Prometheus 是否运行
docker-compose ps prometheus

# 检查网络连接
docker-compose exec grafana ping prometheus
```

### 3. 日志未显示

```bash
# 检查 Promtail 状态
docker-compose logs promtail

# 检查 Loki 状态
docker-compose logs loki

# 验证日志路径
docker-compose exec promtail ls -la /var/lib/docker/containers
```

## 最佳实践

1. **定期审查告警规则**: 避免告警疲劳
2. **使用标签**: 便于过滤和聚合
3. **文档化指标**: 记录每个指标的含义
4. **设置合理的阈值**: 基于历史数据调整
5. **测试告警**: 定期验证告警是否正常工作
6. **备份配置**: 定期备份 Grafana 仪表板和 Prometheus 配置

## 安全建议

1. **修改默认密码**: 首次部署后立即修改
2. **启用 HTTPS**: 生产环境使用 TLS
3. **限制访问**: 使用防火墙或反向代理
4. **定期更新**: 保持组件版本最新
5. **审计日志**: 记录访问和操作日志

## 参考资源

- [Prometheus 文档](https://prometheus.io/docs/)
- [Grafana 文档](https://grafana.com/docs/)
- [Loki 文档](https://grafana.com/docs/loki/latest/)
- [AlertManager 文档](https://prometheus.io/docs/alerting/latest/alertmanager/)

# AI意图路由模块实现文档

## 概述

本模块实现了基于OpenAI协议的AI意图路由系统，是Admin Agent项目的核心功能。

## 功能特性

### 1. 意图分类
- ✅ 自动判断用户输入是知识问答还是工单生成
- ✅ 使用Function Calling提取结构化信息
- ✅ 返回置信度评分

### 2. 知识问答
- ✅ Chroma向量数据库检索
- ✅ 基于检索结果生成答案
- ✅ 支持知识库同步

### 3. 工单生成
- ✅ 多模态输入处理（文本+图片）
- ✅ 自动提取工单结构化字段
- ✅ 智能判断审批流程

### 4. 动态配置
- ✅ 从数据库读取大模型配置
- ✅ 支持切换不同的OpenAI兼容模型
- ✅ 无需重启服务即可更新配置

## 文件结构

```
app/
├── services/
│   ├── ai_service.py          # AI服务层（OpenAI客户端封装）
│   └── vector_store.py        # 向量存储服务（Chroma集成）
└── api/v1/
    └── ai_agent.py            # AI Agent API路由
```

## 核心组件

### 1. AIService (ai_service.py)

**主要方法：**

```python
class AIService:
    async def get_client(db: Session) -> AsyncOpenAI
        # 从数据库读取配置，创建OpenAI客户端
    
    async def classify_intent(user_input: str, db: Session) -> Dict
        # 意图分类：knowledge_qa 或 ticket_generation
    
    async def generate_answer(question: str, context: str, db: Session) -> str
        # 基于知识库上下文生成答案
    
    async def parse_ticket(user_input: str, image_urls: List[str], db: Session) -> Dict
        # 解析工单信息（支持多模态）
```

### 2. VectorStoreService (vector_store.py)

**主要方法：**

```python
class VectorStoreService:
    async def generate_embedding(text: str, db: Session) -> List[float]
        # 生成文本向量
    
    async def add_knowledge(knowledge_id: int, title: str, content: str, db: Session) -> bool
        # 添加知识到向量库
    
    async def search_knowledge(query: str, db: Session, top_k: int) -> List[Dict]
        # 向量检索相关知识
    
    async def sync_all_knowledge(db: Session) -> int
        # 同步所有知识库到向量数据库
```

## API接口

### 1. AI聊天接口

```http
POST /api/v1/ai-agent/chat
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "我的电脑显示器坏了，需要报修",
  "image_urls": ["https://example.com/image1.jpg"]  // 可选
}
```

**响应（知识问答）：**
```json
{
  "intent_type": "knowledge_qa",
  "response": "根据公司规定，WiFi密码是...",
  "confidence": 0.95
}
```

**响应（工单生成）：**
```json
{
  "intent_type": "ticket_generation",
  "response": "已为您创建工单 #123\n\n工单类型：报修\n描述：电脑显示器故障\n紧急程度：normal\n\n需要主管审批",
  "ticket_id": 123,
  "confidence": 0.92
}
```

### 2. 知识库同步接口

```http
POST /api/v1/ai-agent/knowledge/sync
Authorization: Bearer <admin_token>
```

**响应：**
```json
{
  "message": "成功同步 50 条知识到向量数据库",
  "count": 50
}
```

### 3. 知识库搜索接口

```http
GET /api/v1/ai-agent/knowledge/search?query=WiFi密码&top_k=3
Authorization: Bearer <access_token>
```

**响应：**
```json
{
  "query": "WiFi密码",
  "results": [
    {
      "id": 1,
      "title": "WiFi连接指南",
      "content": "公司WiFi密码是...",
      "category": "IT支持",
      "similarity": 0.89
    }
  ],
  "count": 1
}
```

## 工作流程

### 知识问答流程

```
用户输入
    ↓
意图分类 (AI Service)
    ↓
判断为 knowledge_qa
    ↓
向量检索 (Vector Store)
    ↓
检索Top K相关知识
    ↓
生成答案 (AI Service)
    ↓
返回答案给用户
```

### 工单生成流程

```
用户输入 (文本 + 图片)
    ↓
意图分类 (AI Service)
    ↓
判断为 ticket_generation
    ↓
多模态解析 (AI Service)
    ↓
提取结构化信息:
  - 工单类型
  - 物品名称
  - 问题描述
  - 紧急程度
  - 预估费用
    ↓
判断审批流程:
  - 费用 > 1000元 → 需要审批
  - 费用 ≤ 1000元 → 无需审批
    ↓
创建Ticket记录
    ↓
返回工单ID给用户
```

## 配置说明

### 数据库配置（SysConfig表）

需要在SysConfig表中配置以下项：

```sql
INSERT INTO sys_config (config_key, config_value, description, category) VALUES
('LLM_API_KEY', 'sk-xxx', '大模型API密钥', 'llm'),
('LLM_BASE_URL', 'https://api.openai.com/v1', '大模型API基础URL', 'llm'),
('LLM_MODEL_NAME', 'gpt-4o', '模型名称', 'llm'),
('LLM_TEMPERATURE', '0.7', '温度参数', 'llm'),
('LLM_MAX_TOKENS', '1000', '最大token数', 'llm'),
('EMBEDDING_MODEL', 'text-embedding-3-small', '向量化模型', 'llm'),
('VECTOR_DB_PATH', './chroma_db', '向量数据库路径', 'vector');
```

### 环境变量（.env文件）

```env
# OpenAI配置（默认值，可在数据库中覆盖）
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

## 使用示例

### 1. 知识问答

```python
# 用户问题
user_message = "WiFi密码是多少？"

# 调用AI接口
response = await chat(
    ChatRequest(message=user_message),
    current_user=user,
    db=db
)

# 响应
print(response.intent_type)  # "knowledge_qa"
print(response.response)     # "根据公司规定，WiFi密码是..."
```

### 2. 工单生成

```python
# 用户请求
user_message = "我的电脑显示器坏了，屏幕一直闪烁，需要尽快修理"
image_urls = ["https://example.com/broken_monitor.jpg"]

# 调用AI接口
response = await chat(
    ChatRequest(
        message=user_message,
        image_urls=image_urls
    ),
    current_user=user,
    db=db
)

# 响应
print(response.intent_type)  # "ticket_generation"
print(response.ticket_id)    # 123
print(response.response)     # "已为您创建工单 #123..."
```

### 3. 知识库管理

```python
# 添加新知识
knowledge = KnowledgeBase(
    title="WiFi连接指南",
    content="公司WiFi密码是CompanyWiFi2024...",
    category="IT支持"
)
db.add(knowledge)
db.commit()

# 同步到向量库
await vector_store_service.add_knowledge(
    knowledge_id=knowledge.id,
    title=knowledge.title,
    content=knowledge.content,
    db=db
)
```

## 多模态支持

### 图片识别

AI模块支持处理图片输入，可以识别图片中的设备故障、物品信息等：

```python
# 用户上传图片
image_url = "https://example.com/broken_device.jpg"

# AI会分析图片内容
ticket_info = await ai_service.parse_ticket(
    user_input="这个设备坏了",
    image_urls=[image_url],
    db=db
)

# 提取的信息会包含图片中识别的内容
print(ticket_info)
# {
#   "ticket_type": "报修",
#   "item_name": "打印机",
#   "description": "打印机卡纸，无法正常工作",
#   "urgency": "normal"
# }
```

## 性能优化

### 1. 向量检索优化

- 使用Chroma的持久化存储
- 批量同步知识库
- 缓存常用查询结果

### 2. AI调用优化

- 异步调用OpenAI API
- 设置合理的timeout
- 实现降级策略

### 3. 配置缓存

- 缓存数据库配置
- 配置变更时自动刷新客户端

## 错误处理

### 1. AI调用失败

```python
try:
    result = await ai_service.classify_intent(user_input, db)
except Exception as e:
    # 降级处理：默认为知识问答
    result = {
        "intent_type": "knowledge_qa",
        "confidence": 0.5,
        "error": str(e)
    }
```

### 2. 向量检索失败

```python
try:
    results = await vector_store_service.search_knowledge(query, db)
except Exception as e:
    # 返回空结果
    results = []
    logger.error(f"Vector search failed: {e}")
```

## 测试

### 单元测试

```python
import pytest
from app.services.ai_service import ai_service

@pytest.mark.asyncio
async def test_intent_classification():
    result = await ai_service.classify_intent(
        user_input="WiFi密码是多少？",
        db=db
    )
    assert result["intent_type"] == "knowledge_qa"
    assert result["confidence"] > 0.5

@pytest.mark.asyncio
async def test_ticket_parsing():
    result = await ai_service.parse_ticket(
        user_input="我的电脑坏了，需要维修",
        image_urls=None,
        db=db
    )
    assert result["ticket_type"] == "报修"
    assert "description" in result
```

### 集成测试

```bash
# 测试AI聊天接口
curl -X POST http://localhost:8000/api/v1/ai-agent/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "WiFi密码是多少？"
  }'

# 测试知识库同步
curl -X POST http://localhost:8000/api/v1/ai-agent/knowledge/sync \
  -H "Authorization: Bearer <admin_token>"
```

## 监控与日志

### 关键指标

- AI调用成功率
- 平均响应时间
- 意图分类准确率
- 向量检索命中率

### 日志记录

```python
logger.info(f"Intent classification: {intent_type}, confidence: {confidence}")
logger.info(f"Created ticket #{ticket_id} for user {user.username}")
logger.error(f"AI service failed: {error}")
```

## 后续优化

- [ ] 实现流式响应（SSE）
- [ ] 添加对话历史记录
- [ ] 支持多轮对话
- [ ] 优化Prompt工程
- [ ] 添加A/B测试功能
- [ ] 实现意图分类模型微调

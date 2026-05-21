from openai import AsyncOpenAI
from typing import Optional, List, Dict, Any
import logging
from sqlmodel import Session, select

from ..core.config import settings
from ..models import SysConfig, ConfigKeys

logger = logging.getLogger(__name__)


class AIService:
    """
    AI服务层
    封装OpenAI客户端，支持动态配置切换不同的大模型
    """

    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None
        self._current_config: Dict[str, str] = {}

    async def get_client(self, db: Session) -> AsyncOpenAI:
        """
        获取OpenAI客户端
        从数据库读取配置，支持动态切换大模型

        Args:
            db: 数据库会话

        Returns:
            AsyncOpenAI: OpenAI异步客户端
        """
        # 从数据库读取最新配置
        config = await self._load_config(db)

        # 如果配置发生变化，重新创建客户端
        if config != self._current_config:
            logger.info("AI configuration changed, recreating client")
            self._client = AsyncOpenAI(
                api_key=config.get(ConfigKeys.LLM_API_KEY, settings.OPENAI_API_KEY),
                base_url=config.get(ConfigKeys.LLM_BASE_URL, settings.OPENAI_BASE_URL),
            )
            self._current_config = config

        return self._client

    async def _load_config(self, db: Session) -> Dict[str, str]:
        """
        从数据库加载AI配置

        Args:
            db: 数据库会话

        Returns:
            Dict[str, str]: 配置字典
        """
        config_keys = [
            ConfigKeys.LLM_API_KEY,
            ConfigKeys.LLM_BASE_URL,
            ConfigKeys.LLM_MODEL_NAME,
            ConfigKeys.LLM_TEMPERATURE,
            ConfigKeys.LLM_MAX_TOKENS,
        ]

        config = {}
        for key in config_keys:
            statement = select(SysConfig).where(SysConfig.config_key == key)
            result = db.exec(statement).first()
            if result:
                config[key] = result.config_value

        return config

    async def classify_intent(
        self,
        user_input: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        意图分类
        判断用户输入是知识问答还是工单生成

        Args:
            user_input: 用户输入文本
            db: 数据库会话

        Returns:
            Dict: 包含intent_type和相关信息的字典
                - intent_type: "knowledge_qa" 或 "ticket_generation"
                - confidence: 置信度 (0-1)
                - extracted_info: 提取的结构化信息
        """
        client = await self.get_client(db)
        config = self._current_config

        # 使用Function Calling进行意图分类
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "classify_intent",
                    "description": "分类用户意图：知识问答或工单生成",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "intent_type": {
                                "type": "string",
                                "enum": ["knowledge_qa", "ticket_generation"],
                                "description": "意图类型：knowledge_qa(知识问答)或ticket_generation(工单生成)"
                            },
                            "confidence": {
                                "type": "number",
                                "description": "置信度，0-1之间"
                            },
                            "ticket_type": {
                                "type": "string",
                                "enum": ["采购", "报修", "申领", "咨询"],
                                "description": "如果是工单，工单类型"
                            },
                            "urgency": {
                                "type": "string",
                                "enum": ["normal", "urgent", "critical"],
                                "description": "紧急程度"
                            },
                            "estimated_cost": {
                                "type": "number",
                                "description": "预估费用（元）"
                            }
                        },
                        "required": ["intent_type", "confidence"]
                    }
                }
            }
        ]

        system_prompt = """你是一个企业行政助手，负责分析员工的请求。

判断规则：
1. 知识问答(knowledge_qa)：询问规章制度、流程、信息查询等
   - 例如："WiFi密码是多少？"、"报销流程是什么？"、"会议室在哪里？"

2. 工单生成(ticket_generation)：需要行政处理的具体事项
   - 采购：购买物品、设备等
   - 报修：设备故障、设施损坏等
   - 申领：领用办公用品、资产等
   - 咨询：需要行政专员处理的咨询

请分析用户输入并返回意图分类。"""

        try:
            response = await client.chat.completions.create(
                model=config.get(ConfigKeys.LLM_MODEL_NAME, settings.OPENAI_MODEL),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "classify_intent"}},
                temperature=float(config.get(ConfigKeys.LLM_TEMPERATURE, "0.3"))
            )

            # 解析Function Calling结果
            tool_call = response.choices[0].message.tool_calls[0]
            import json
            result = json.loads(tool_call.function.arguments)

            logger.info(f"Intent classification result: {result}")
            return result

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            # 降级处理：默认为知识问答
            return {
                "intent_type": "knowledge_qa",
                "confidence": 0.5,
                "error": str(e)
            }

    async def generate_answer(
        self,
        question: str,
        context: str,
        db: Session
    ) -> str:
        """
        生成知识问答的答案

        Args:
            question: 用户问题
            context: 检索到的知识库内容
            db: 数据库会话

        Returns:
            str: 生成的答案
        """
        client = await self.get_client(db)
        config = self._current_config

        system_prompt = """你是一个专业的企业行政助手。

基于提供的知识库内容回答用户问题：
1. 回答要准确、简洁、专业
2. 如果知识库中没有相关信息，诚实告知用户
3. 使用友好的语气
4. 如果涉及流程，可以分步骤说明"""

        user_prompt = f"""知识库内容：
{context}

用户问题：{question}

请基于知识库内容回答用户问题。"""

        try:
            response = await client.chat.completions.create(
                model=config.get(ConfigKeys.LLM_MODEL_NAME, settings.OPENAI_MODEL),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=float(config.get(ConfigKeys.LLM_TEMPERATURE, "0.7")),
                max_tokens=int(config.get(ConfigKeys.LLM_MAX_TOKENS, "1000"))
            )

            answer = response.choices[0].message.content
            logger.info(f"Generated answer for question: {question[:50]}...")
            return answer

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return "抱歉，我暂时无法回答这个问题。请联系行政人员获取帮助。"

    async def parse_ticket(
        self,
        user_input: str,
        image_urls: Optional[List[str]],
        db: Session
    ) -> Dict[str, Any]:
        """
        解析工单信息
        从用户输入中提取结构化的工单字段

        Args:
            user_input: 用户输入文本
            image_urls: 图片URL列表（可选）
            db: 数据库会话

        Returns:
            Dict: 结构化的工单信息
        """
        client = await self.get_client(db)
        config = self._current_config

        # 构建消息（支持多模态）
        messages = [
            {
                "role": "system",
                "content": """你是一个工单信息提取助手。从用户描述中提取以下信息：
1. 工单类型（采购/报修/申领/咨询）
2. 物品/设备名称
3. 问题描述
4. 紧急程度
5. 预估费用（如果提到）
6. 其他相关信息"""
            }
        ]

        # 文本内容
        user_content = [{"type": "text", "text": user_input}]

        # 如果有图片，添加图片内容（多模态）
        if image_urls:
            for url in image_urls:
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": url}
                })

        messages.append({"role": "user", "content": user_content})

        # Function Calling定义
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "extract_ticket_info",
                    "description": "提取工单结构化信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_type": {
                                "type": "string",
                                "enum": ["采购", "报修", "申领", "咨询"]
                            },
                            "item_name": {
                                "type": "string",
                                "description": "物品或设备名称"
                            },
                            "description": {
                                "type": "string",
                                "description": "详细描述"
                            },
                            "urgency": {
                                "type": "string",
                                "enum": ["normal", "urgent", "critical"]
                            },
                            "estimated_cost": {
                                "type": "number",
                                "description": "预估费用（元）"
                            },
                            "location": {
                                "type": "string",
                                "description": "位置信息（如果相关）"
                            }
                        },
                        "required": ["ticket_type", "description"]
                    }
                }
            }
        ]

        try:
            response = await client.chat.completions.create(
                model=config.get(ConfigKeys.LLM_MODEL_NAME, settings.OPENAI_MODEL),
                messages=messages,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "extract_ticket_info"}},
                temperature=float(config.get(ConfigKeys.LLM_TEMPERATURE, "0.3"))
            )

            # 解析结果
            tool_call = response.choices[0].message.tool_calls[0]
            import json
            ticket_info = json.loads(tool_call.function.arguments)

            logger.info(f"Parsed ticket info: {ticket_info}")
            return ticket_info

        except Exception as e:
            logger.error(f"Ticket parsing failed: {e}")
            # 降级处理：返回基本信息
            return {
                "ticket_type": "咨询",
                "description": user_input,
                "urgency": "normal",
                "error": str(e)
            }


# 全局AI服务实例
ai_service = AIService()

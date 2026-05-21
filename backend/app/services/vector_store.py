from typing import List, Dict, Any, Optional
import logging
from openai import AsyncOpenAI
import chromadb
from chromadb.config import Settings as ChromaSettings
from sqlmodel import Session, select

from ..core.config import settings
from ..models import KnowledgeBase, SysConfig, ConfigKeys

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    向量存储服务
    使用Chroma进行知识库的向量检索
    """

    def __init__(self):
        self._chroma_client: Optional[chromadb.Client] = None
        self._collection = None
        self._openai_client: Optional[AsyncOpenAI] = None
        self._openai_config: Dict[str, str] = {}

    def _load_openai_config(self, db: Session) -> Dict[str, str]:
        statement = select(SysConfig).where(
            SysConfig.config_key == ConfigKeys.LLM_API_KEY
        )
        api_key_config = db.exec(statement).first()

        statement = select(SysConfig).where(
            SysConfig.config_key == ConfigKeys.EMBEDDING_BASE_URL
        )
        base_url_config = db.exec(statement).first()

        return {
            ConfigKeys.LLM_API_KEY: api_key_config.config_value if api_key_config else settings.OPENAI_API_KEY,
            ConfigKeys.EMBEDDING_BASE_URL: base_url_config.config_value if base_url_config else settings.OPENAI_BASE_URL,
        }

    def _get_chroma_client(self, db: Session) -> chromadb.Client:
        """
        获取Chroma客户端

        Args:
            db: 数据库会话

        Returns:
            chromadb.Client: Chroma客户端
        """
        if self._chroma_client is None:
            # 从配置读取向量数据库路径
            statement = select(SysConfig).where(
                SysConfig.config_key == ConfigKeys.VECTOR_DB_PATH
            )
            config = db.exec(statement).first()
            db_path = config.config_value if config else "./chroma_db"

            self._chroma_client = chromadb.Client(
                ChromaSettings(
                    persist_directory=db_path,
                    anonymized_telemetry=False
                )
            )

            # 获取或创建collection
            self._collection = self._chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "企业行政知识库"}
            )

        return self._chroma_client

    async def _get_openai_client(self, db: Session) -> AsyncOpenAI:
        """
        获取OpenAI客户端用于生成embeddings

        Args:
            db: 数据库会话

        Returns:
            AsyncOpenAI: OpenAI客户端
        """
        config = self._load_openai_config(db)

        if self._openai_client is None or config != self._openai_config:
            # 从配置读取API密钥
            statement = select(SysConfig).where(
                SysConfig.config_key == ConfigKeys.LLM_API_KEY
            )
            api_key_config = db.exec(statement).first()
            api_key = api_key_config.config_value if api_key_config else settings.OPENAI_API_KEY

            statement = select(SysConfig).where(
                SysConfig.config_key == ConfigKeys.EMBEDDING_BASE_URL
            )
            base_url_config = db.exec(statement).first()
            base_url = base_url_config.config_value if base_url_config else settings.OPENAI_BASE_URL

            self._openai_client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
            self._openai_config = config

        return self._openai_client

    async def generate_embedding(
        self,
        text: str,
        db: Session
    ) -> List[float]:
        """
        生成文本的向量表示

        Args:
            text: 输入文本
            db: 数据库会话

        Returns:
            List[float]: 向量表示
        """
        client = await self._get_openai_client(db)

        # 从配置读取embedding模型
        statement = select(SysConfig).where(
            SysConfig.config_key == ConfigKeys.EMBEDDING_MODEL
        )
        config = db.exec(statement).first()
        model = config.config_value if config else "text-embedding-3-small"

        try:
            response = await client.embeddings.create(
                model=model,
                input=text
            )
            embedding = response.data[0].embedding
            return embedding

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    async def add_knowledge(
        self,
        knowledge_id: int,
        title: str,
        content: str,
        db: Session
    ) -> bool:
        """
        添加知识到向量库

        Args:
            knowledge_id: 知识库ID
            title: 标题
            content: 内容
            db: 数据库会话

        Returns:
            bool: 是否成功
        """
        try:
            # 生成embedding
            text = f"{title}\n{content}"
            embedding = await self.generate_embedding(text, db)

            # 获取Chroma客户端
            self._get_chroma_client(db)

            # 添加到collection
            self._collection.add(
                ids=[str(knowledge_id)],
                embeddings=[embedding],
                documents=[content],
                metadatas=[{"title": title, "knowledge_id": knowledge_id}]
            )

            logger.info(f"Added knowledge {knowledge_id} to vector store")
            return True

        except Exception as e:
            logger.error(f"Failed to add knowledge to vector store: {e}")
            return False

    async def search_knowledge(
        self,
        query: str,
        db: Session,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        搜索相关知识

        Args:
            query: 查询文本
            db: 数据库会话
            top_k: 返回top K个结果

        Returns:
            List[Dict]: 搜索结果列表
        """
        try:
            # 生成查询的embedding
            query_embedding = await self.generate_embedding(query, db)

            # 获取Chroma客户端
            self._get_chroma_client(db)

            # 向量检索
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            # 格式化结果
            formatted_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    knowledge_id = int(results['ids'][0][i])
                    distance = results['distances'][0][i] if 'distances' in results else None
                    metadata = results['metadatas'][0][i] if 'metadatas' in results else {}
                    document = results['documents'][0][i] if 'documents' in results else ""

                    # 从数据库获取完整信息
                    statement = select(KnowledgeBase).where(
                        KnowledgeBase.id == knowledge_id
                    )
                    knowledge = db.exec(statement).first()

                    if knowledge:
                        formatted_results.append({
                            "id": knowledge.id,
                            "title": knowledge.title,
                            "content": knowledge.content,
                            "category": knowledge.category,
                            "similarity": 1 - distance if distance else None,
                            "document": document
                        })

            logger.info(f"Found {len(formatted_results)} knowledge items for query: {query[:50]}...")
            return formatted_results

        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return []

    async def sync_all_knowledge(self, db: Session) -> int:
        """
        同步所有知识库到向量数据库

        Args:
            db: 数据库会话

        Returns:
            int: 同步的知识条目数
        """
        try:
            # 获取所有激活的知识
            statement = select(KnowledgeBase).where(KnowledgeBase.is_active == True)
            knowledge_list = db.exec(statement).all()

            count = 0
            for knowledge in knowledge_list:
                success = await self.add_knowledge(
                    knowledge_id=knowledge.id,
                    title=knowledge.title,
                    content=knowledge.content,
                    db=db
                )
                if success:
                    count += 1

            logger.info(f"Synced {count} knowledge items to vector store")
            return count

        except Exception as e:
            logger.error(f"Knowledge sync failed: {e}")
            return 0

    def delete_knowledge(self, knowledge_id: int, db: Session) -> bool:
        """
        从向量库删除知识

        Args:
            knowledge_id: 知识库ID
            db: 数据库会话

        Returns:
            bool: 是否成功
        """
        try:
            self._get_chroma_client(db)
            self._collection.delete(ids=[str(knowledge_id)])
            logger.info(f"Deleted knowledge {knowledge_id} from vector store")
            return True

        except Exception as e:
            logger.error(f"Failed to delete knowledge from vector store: {e}")
            return False


# 全局向量存储服务实例
vector_store_service = VectorStoreService()

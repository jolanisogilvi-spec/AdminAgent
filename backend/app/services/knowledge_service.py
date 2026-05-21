"""知识库服务 - 管理知识库的 CRUD 和向量检索"""

from typing import List, Optional, Dict
from sqlmodel import Session, select
import logging

from app.models import KnowledgeBase
from app.services.ai_service import AIService
from app.core.chroma import ChromaService

logger = logging.getLogger(__name__)


class KnowledgeService:
    """
    知识库服务类
    处理知识库的增删改查和向量检索
    """

    def __init__(self, db: Session, ai_service: AIService, chroma: ChromaService):
        self.db = db
        self.ai_service = ai_service
        self.chroma = chroma

    async def create_knowledge(self, title: str, content: str, category: str, created_by: int) -> KnowledgeBase:
        """
        创建知识库条目
        自动生成向量并存储到 Chroma
        """
        try:
            # 生成向量
            embedding = await self.ai_service.generate_embedding(content)

            # 创建数据库记录
            knowledge = KnowledgeBase(
                title=title,
                content=content,
                category=category,
                created_by=created_by,
            )
            self.db.add(knowledge)
            self.db.commit()
            self.db.refresh(knowledge)

            # 存储到向量库
            if embedding:
                self.chroma.add_document(
                    doc_id=str(knowledge.id),
                    text=content,
                    embedding=embedding,
                    metadata={
                        "title": title,
                        "category": category,
                        "id": knowledge.id,
                    },
                )

            logger.info(f"Created knowledge: {knowledge.id}")
            return knowledge

        except Exception as e:
            logger.error(f"Failed to create knowledge: {e}")
            self.db.rollback()
            raise

    def get_knowledge(self, knowledge_id: int) -> Optional[KnowledgeBase]:
        """
        获取单个知识库条目
        """
        stmt = select(KnowledgeBase).where(KnowledgeBase.id == knowledge_id)
        knowledge = self.db.exec(stmt).first()

        if knowledge:
            # 增加查看次数
            knowledge.view_count += 1
            self.db.add(knowledge)
            self.db.commit()

        return knowledge

    def list_knowledge(
        self,
        category: Optional[str] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 20,
    ) -> List[KnowledgeBase]:
        """
        列出知识库条目
        支持分类过滤和分页
        """
        stmt = select(KnowledgeBase).where(KnowledgeBase.is_active == is_active)

        if category:
            stmt = stmt.where(KnowledgeBase.category == category)

        stmt = stmt.offset(skip).limit(limit).order_by(KnowledgeBase.created_at.desc())
        return list(self.db.exec(stmt).all())

    async def update_knowledge(
        self,
        knowledge_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Optional[KnowledgeBase]:
        """
        更新知识库条目
        如果内容变更，重新生成向量
        """
        knowledge = self.get_knowledge(knowledge_id)
        if not knowledge:
            return None

        try:
            update_vector = False

            if title:
                knowledge.title = title
            if content:
                knowledge.content = content
                update_vector = True
            if category:
                knowledge.category = category

            self.db.add(knowledge)
            self.db.commit()
            self.db.refresh(knowledge)

            # 更新向量库
            if update_vector:
                embedding = await self.ai_service.generate_embedding(content)
                if embedding:
                    self.chroma.update_document(
                        doc_id=str(knowledge_id),
                        text=content,
                        embedding=embedding,
                        metadata={
                            "title": knowledge.title,
                            "category": knowledge.category,
                            "id": knowledge.id,
                        },
                    )

            return knowledge

        except Exception as e:
            logger.error(f"Failed to update knowledge {knowledge_id}: {e}")
            self.db.rollback()
            raise

    def delete_knowledge(self, knowledge_id: int) -> bool:
        """
        删除知识库条目（软删除）
        """
        knowledge = self.get_knowledge(knowledge_id)
        if not knowledge:
            return False

        try:
            knowledge.is_active = False
            self.db.add(knowledge)
            self.db.commit()

            # 从向量库删除
            self.chroma.delete_document(str(knowledge_id))

            logger.info(f"Deleted knowledge: {knowledge_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete knowledge {knowledge_id}: {e}")
            self.db.rollback()
            return False

    async def search_knowledge(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        向量相似度搜索
        返回最相关的知识库条目
        """
        try:
            # 生成查询向量
            query_embedding = await self.ai_service.generate_embedding(query)
            if not query_embedding:
                return []

            # 向量搜索
            results = self.chroma.search(query_embedding, n_results=n_results)

            # 补充完整的数据库信息
            enriched_results = []
            for result in results:
                knowledge_id = int(result["id"])
                knowledge = self.get_knowledge(knowledge_id)
                if knowledge and knowledge.is_active:
                    enriched_results.append({
                        "id": knowledge.id,
                        "title": knowledge.title,
                        "content": knowledge.content,
                        "category": knowledge.category,
                        "similarity": 1 - result["distance"],  # 转换为相似度
                    })

            return enriched_results

        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return []

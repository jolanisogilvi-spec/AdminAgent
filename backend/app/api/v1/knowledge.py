from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from app.core.chroma import ChromaService, get_chroma
from app.core.database import get_db
from app.models import KnowledgeBase
from app.services.ai_service import ai_service
from app.services.knowledge_service import KnowledgeService

router = APIRouter()


class KnowledgeCreate(BaseModel):
    title: str
    content: str
    category: str


class KnowledgeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None


class KnowledgeSearch(BaseModel):
    query: str
    n_results: int = 5


class KnowledgeResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    view_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


def get_knowledge_service(
    db: Session = Depends(get_db),
    chroma: ChromaService = Depends(get_chroma),
) -> KnowledgeService:
    return KnowledgeService(db, ai_service, chroma)


@router.post("/", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge(
    knowledge_data: KnowledgeCreate,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    return await service.create_knowledge(
        title=knowledge_data.title,
        content=knowledge_data.content,
        category=knowledge_data.category,
        created_by=1,
    )


@router.get("/{knowledge_id}", response_model=KnowledgeResponse)
def get_knowledge(knowledge_id: int, service: KnowledgeService = Depends(get_knowledge_service)):
    knowledge = service.get_knowledge(knowledge_id)
    if not knowledge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge not found")
    return knowledge


@router.get("/", response_model=list[KnowledgeResponse])
def list_knowledge(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    return service.list_knowledge(category=category, skip=skip, limit=limit)


@router.put("/{knowledge_id}", response_model=KnowledgeResponse)
async def update_knowledge(
    knowledge_id: int,
    knowledge_data: KnowledgeUpdate,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    knowledge = await service.update_knowledge(
        knowledge_id=knowledge_id,
        title=knowledge_data.title,
        content=knowledge_data.content,
        category=knowledge_data.category,
    )
    if not knowledge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge not found")
    return knowledge


@router.delete("/{knowledge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge(knowledge_id: int, service: KnowledgeService = Depends(get_knowledge_service)):
    if not service.delete_knowledge(knowledge_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge not found")


@router.post("/search")
async def search_knowledge(
    search_data: KnowledgeSearch,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    results = await service.search_knowledge(
        query=search_data.query,
        n_results=search_data.n_results,
    )
    return {"results": results}

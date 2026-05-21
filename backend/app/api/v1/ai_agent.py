from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.deps import get_current_active_user, require_admin
from app.core.database import get_db
from app.models.enums import ApprovalStatus, ProcessingStatus, TicketType, UrgencyLevel
from app.models.ticket import Ticket
from app.models.user import User
from app.services.approval_service import ApprovalService
from app.services.vector_store import vector_store_service

router = APIRouter(tags=["AI智能体"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    image_urls: Optional[list[str]] = None


class ChatResponse(BaseModel):
    intent_type: str
    response: str
    ticket_id: Optional[int] = None
    confidence: float


def classify_locally(message: str) -> str:
    ticket_keywords = ["报修", "维修", "采购", "购买", "申领", "领用", "坏了", "故障", "需要处理"]
    return "ticket_generation" if any(word in message for word in ticket_keywords) else "knowledge_qa"


def parse_ticket_type(message: str) -> TicketType:
    if "采购" in message or "购买" in message:
        return TicketType.PURCHASE
    if "报修" in message or "维修" in message or "坏了" in message or "故障" in message:
        return TicketType.REPAIR
    if "申领" in message or "领用" in message:
        return TicketType.REQUISITION
    return TicketType.CONSULTATION


def parse_urgency(message: str) -> UrgencyLevel:
    if "紧急" in message or "马上" in message or "立刻" in message:
        return UrgencyLevel.URGENT
    if "尽快" in message or "着急" in message:
        return UrgencyLevel.HIGH
    return UrgencyLevel.NORMAL


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    intent_type = classify_locally(request.message)

    if intent_type == "knowledge_qa":
        results = await vector_store_service.search_knowledge(query=request.message, db=db, top_k=3)
        if results:
            answer = "\n\n".join([f"{item['title']}: {item['content']}" for item in results])
        else:
            answer = "暂未检索到相关知识库内容，请联系行政人员确认。"
        return ChatResponse(intent_type="knowledge_qa", response=answer, confidence=0.65)

    estimated_cost = Decimal("0")
    ticket = Ticket(
        requester_id=current_user.id or 1,
        original_text=request.message,
        attachments=",".join(request.image_urls) if request.image_urls else None,
        ticket_type=parse_ticket_type(request.message),
        estimated_cost=estimated_cost,
        urgency=parse_urgency(request.message),
        approval_status=ApprovalService.determine_approval_status(estimated_cost),
        processing_status=ProcessingStatus.PENDING,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ChatResponse(
        intent_type="ticket_generation",
        response=f"已为你创建工单 #{ticket.id}，行政人员会跟进处理。",
        ticket_id=ticket.id,
        confidence=0.75,
    )


@router.post("/knowledge/sync")
async def sync_knowledge(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_admin(current_user)
    count = await vector_store_service.sync_all_knowledge(db)
    return {"message": f"成功同步 {count} 条知识到向量库", "count": count}


@router.get("/knowledge/search")
async def search_knowledge(
    query: str,
    top_k: int = 3,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    results = await vector_store_service.search_knowledge(query=query, db=db, top_k=top_k)
    return {"query": query, "results": results, "count": len(results)}

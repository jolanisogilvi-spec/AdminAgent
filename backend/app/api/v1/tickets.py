from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.api.deps import get_current_active_user
from app.core.database import get_session
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
from app.services.ticket_service import TicketService

router = APIRouter(tags=["工单管理"])

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: TicketCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """创建工单"""
    ticket = TicketService.create_ticket(session, ticket_data, current_user.id)
    return ticket

@router.get("/", response_model=List[TicketResponse])
def get_tickets(
    skip: int = 0,
    limit: int = 100,
    processing_status: str = None,
    session: Session = Depends(get_session),
):
    """获取工单列表"""
    tickets = TicketService.get_tickets(
        session, skip=skip, limit=limit, processing_status=processing_status
    )
    return tickets

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, session: Session = Depends(get_session)):
    """获取单个工单"""
    ticket = TicketService.get_ticket(session, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="工单不存在"
        )
    return ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    session: Session = Depends(get_session),
):
    """更新工单"""
    ticket = TicketService.update_ticket(session, ticket_id, ticket_data)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="工单不存在"
        )
    return ticket

@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, session: Session = Depends(get_session)):
    """删除工单"""
    success = TicketService.delete_ticket(session, ticket_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="工单不存在"
        )
    return None

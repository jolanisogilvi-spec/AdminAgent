from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.api.deps import get_current_active_user
from app.core.database import get_session
from app.models.user import User
from app.schemas.ticket import TicketResponse
from app.schemas.approval import ApprovalRecordUpdate
from app.services.approval_service import ApprovalService

router = APIRouter(tags=["审批管理"])

@router.get("/pending", response_model=List[TicketResponse])
def get_pending_approvals(
    approval_type: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """获取待审批工单列表

    Args:
        approval_type: 审批类型 (manager/finance)
    """
    if approval_type not in ["manager", "finance"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="审批类型必须是 manager 或 finance"
        )

    tickets = ApprovalService.get_pending_approvals(
        session, current_user.id, approval_type, skip, limit
    )
    return tickets

@router.post("/tickets/{ticket_id}/approve", response_model=TicketResponse)
def approve_ticket(
    ticket_id: int,
    approval_type: str,
    approval_data: ApprovalRecordUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """审批通过工单

    Args:
        ticket_id: 工单ID
        approval_type: 审批类型 (manager/finance)
        approval_data: 审批数据（包含意见）
    """
    if approval_type not in ["manager", "finance"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="审批类型必须是 manager 或 finance"
        )

    ticket = ApprovalService.approve_ticket(
        session, ticket_id, current_user.id, approval_type, approval_data.comment
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )

    return ticket

@router.post("/tickets/{ticket_id}/reject", response_model=TicketResponse)
def reject_ticket(
    ticket_id: int,
    approval_data: ApprovalRecordUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """驳回工单

    Args:
        ticket_id: 工单ID
        approval_data: 审批数据（必须包含驳回理由）
    """
    if not approval_data.comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="驳回工单必须填写理由"
        )

    ticket = ApprovalService.reject_ticket(
        session, ticket_id, current_user.id, approval_data.comment
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )

    return ticket

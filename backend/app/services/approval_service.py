from typing import List, Optional
from sqlmodel import Session, select
from decimal import Decimal

from app.models.ticket import Ticket
from app.models.enums import ApprovalStatus, ProcessingStatus

class ApprovalService:
    """审批流程服务"""

    # 审批阈值配置
    MANAGER_APPROVAL_THRESHOLD = Decimal("1000.00")  # 主管审批阈值
    FINANCE_APPROVAL_THRESHOLD = Decimal("5000.00")  # 财务审批阈值

    @staticmethod
    def determine_approval_status(estimated_cost: Decimal) -> ApprovalStatus:
        """根据预估费用确定审批状态"""
        if estimated_cost >= ApprovalService.FINANCE_APPROVAL_THRESHOLD:
            return ApprovalStatus.PENDING_FINANCE
        elif estimated_cost >= ApprovalService.MANAGER_APPROVAL_THRESHOLD:
            return ApprovalStatus.PENDING_MANAGER
        else:
            return ApprovalStatus.NO_APPROVAL

    @staticmethod
    def approve_ticket(
        session: Session,
        ticket_id: int,
        approver_id: int,
        approval_type: str,
        comment: Optional[str] = None
    ) -> Optional[Ticket]:
        """审批通过工单"""
        ticket = session.get(Ticket, ticket_id)
        if not ticket:
            return None

        # 更新审批状态
        if approval_type == "manager":
            if ticket.approval_status == ApprovalStatus.PENDING_MANAGER:
                # 检查是否需要财务审批
                if ticket.estimated_cost >= ApprovalService.FINANCE_APPROVAL_THRESHOLD:
                    ticket.approval_status = ApprovalStatus.PENDING_FINANCE
                else:
                    ticket.approval_status = ApprovalStatus.APPROVED
                    ticket.processing_status = ProcessingStatus.PENDING

        elif approval_type == "finance":
            if ticket.approval_status == ApprovalStatus.PENDING_FINANCE:
                ticket.approval_status = ApprovalStatus.APPROVED
                ticket.processing_status = ProcessingStatus.PENDING

        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        return ticket

    @staticmethod
    def reject_ticket(
        session: Session,
        ticket_id: int,
        approver_id: int,
        comment: str
    ) -> Optional[Ticket]:
        """驳回工单"""
        ticket = session.get(Ticket, ticket_id)
        if not ticket:
            return None

        ticket.approval_status = ApprovalStatus.REJECTED
        ticket.processing_status = ProcessingStatus.COMPLETED

        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        return ticket

    @staticmethod
    def get_pending_approvals(
        session: Session,
        approver_id: int,
        approval_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ticket]:
        """获取待审批工单列表"""
        statement = select(Ticket)

        if approval_type == "manager":
            statement = statement.where(
                Ticket.approval_status == ApprovalStatus.PENDING_MANAGER
            )
        elif approval_type == "finance":
            statement = statement.where(
                Ticket.approval_status == ApprovalStatus.PENDING_FINANCE
            )

        statement = statement.offset(skip).limit(limit)
        results = session.exec(statement)
        return results.all()

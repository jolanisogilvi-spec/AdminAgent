from typing import List, Optional
from sqlmodel import Session, select
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.services.approval_service import ApprovalService

class TicketService:
    @staticmethod
    def create_ticket(session: Session, ticket_data: TicketCreate, requester_id: int) -> Ticket:
        """创建工单"""
        ticket = Ticket(
            **ticket_data.model_dump(),
            requester_id=requester_id,
        )

        # 自动设置审批状态
        ticket.approval_status = ApprovalService.determine_approval_status(
            ticket.estimated_cost
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        return ticket

    @staticmethod
    def get_ticket(session: Session, ticket_id: int) -> Optional[Ticket]:
        """获取单个工单"""
        return session.get(Ticket, ticket_id)

    @staticmethod
    def get_tickets(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        requester_id: Optional[int] = None,
        processing_status: Optional[str] = None,
    ) -> List[Ticket]:
        """获取工单列表"""
        statement = select(Ticket)

        if requester_id:
            statement = statement.where(Ticket.requester_id == requester_id)

        if processing_status:
            statement = statement.where(Ticket.processing_status == processing_status)

        statement = statement.offset(skip).limit(limit)
        results = session.exec(statement)
        return results.all()

    @staticmethod
    def update_ticket(
        session: Session, ticket_id: int, ticket_data: TicketUpdate
    ) -> Optional[Ticket]:
        """更新工单"""
        ticket = session.get(Ticket, ticket_id)
        if not ticket:
            return None

        update_data = ticket_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ticket, key, value)

        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        return ticket

    @staticmethod
    def delete_ticket(session: Session, ticket_id: int) -> bool:
        """删除工单"""
        ticket = session.get(Ticket, ticket_id)
        if not ticket:
            return False

        session.delete(ticket)
        session.commit()
        return True

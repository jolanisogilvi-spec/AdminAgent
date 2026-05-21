"""Ticket Repository - 工单数据访问层

提供工单相关的数据库操作
"""

from typing import List, Optional
from sqlmodel import Session, select, and_, or_
from datetime import datetime

from app.models import Ticket, TicketType, ApprovalStatus, ProcessingStatus
from .base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    """工单Repository"""

    def __init__(self, session: Session):
        super().__init__(Ticket, session)

    def get_by_creator(
        self,
        creator_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ticket]:
        """
        获取指定用户创建的工单

        Args:
            creator_id: 创建人ID
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            工单列表
        """
        statement = (
            select(Ticket)
            .where(Ticket.creator_id == creator_id)
            .order_by(Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def get_by_status(
        self,
        processing_status: ProcessingStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ticket]:
        """
        根据处理状态获取工单

        Args:
            processing_status: 处理状态
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            工单列表
        """
        statement = (
            select(Ticket)
            .where(Ticket.processing_status == processing_status)
            .order_by(Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def get_pending_approval(
        self,
        approval_status: Optional[ApprovalStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ticket]:
        """
        获取待审批的工单

        Args:
            approval_status: 审批状态（可选，默认获取所有待审批）
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            工单列表
        """
        if approval_status:
            statement = select(Ticket).where(Ticket.approval_status == approval_status)
        else:
            statement = select(Ticket).where(
                or_(
                    Ticket.approval_status == ApprovalStatus.PENDING_MANAGER,
                    Ticket.approval_status == ApprovalStatus.PENDING_FINANCE
                )
            )

        statement = (
            statement
            .order_by(Ticket.urgency_level.desc(), Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def get_by_type(
        self,
        ticket_type: TicketType,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ticket]:
        """
        根据工单类型获取工单

        Args:
            ticket_type: 工单类型
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            工单列表
        """
        statement = (
            select(Ticket)
            .where(Ticket.ticket_type == ticket_type)
            .order_by(Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def get_assigned_to_admin(
        self,
        admin_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ticket]:
        """
        获取分配给指定行政人员的工单

        Args:
            admin_id: 行政人员ID
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            工单列表
        """
        statement = (
            select(Ticket)
            .where(Ticket.assigned_admin_id == admin_id)
            .where(Ticket.processing_status != ProcessingStatus.COMPLETED)
            .order_by(Ticket.urgency_level.desc(), Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def search(
        self,
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ticket]:
        """
        搜索工单（标题和描述）

        Args:
            keyword: 搜索关键词
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            工单列表
        """
        search_pattern = f"%{keyword}%"
        statement = (
            select(Ticket)
            .where(
                or_(
                    Ticket.title.ilike(search_pattern),
                    Ticket.description.ilike(search_pattern),
                    Ticket.original_text.ilike(search_pattern)
                )
            )
            .order_by(Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def get_statistics_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """
        获取指定日期范围内的工单统计

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            统计数据字典
        """
        statement = select(Ticket).where(
            and_(
                Ticket.created_at >= start_date,
                Ticket.created_at <= end_date
            )
        )
        tickets = self.session.exec(statement).all()

        # 统计各类型工单数量
        type_counts = {}
        for ticket_type in TicketType:
            type_counts[ticket_type.value] = sum(
                1 for t in tickets if t.ticket_type == ticket_type
            )

        # 统计各状态工单数量
        status_counts = {}
        for status in ProcessingStatus:
            status_counts[status.value] = sum(
                1 for t in tickets if t.processing_status == status
            )

        # 计算平均处理时间（已完成的工单）
        completed_tickets = [
            t for t in tickets
            if t.processing_status == ProcessingStatus.COMPLETED and t.closed_at
        ]
        avg_processing_time = None
        if completed_tickets:
            total_time = sum(
                (t.closed_at - t.created_at).total_seconds()
                for t in completed_tickets
            )
            avg_processing_time = total_time / len(completed_tickets) / 3600  # 小时

        return {
            "total_count": len(tickets),
            "type_counts": type_counts,
            "status_counts": status_counts,
            "avg_processing_time_hours": avg_processing_time,
            "total_estimated_cost": sum(
                t.estimated_cost or 0 for t in tickets
            ),
            "total_actual_cost": sum(
                t.actual_cost or 0 for t in tickets
            )
        }

    def update_approval_status(
        self,
        ticket_id: int,
        approval_status: ApprovalStatus,
        approver_id: int,
        notes: Optional[str] = None
    ) -> Optional[Ticket]:
        """
        更新工单审批状态

        Args:
            ticket_id: 工单ID
            approval_status: 新的审批状态
            approver_id: 审批人ID
            notes: 审批备注

        Returns:
            更新后的工单或None
        """
        ticket = self.get_by_id(ticket_id)
        if not ticket:
            return None

        ticket.approval_status = approval_status
        if notes:
            ticket.approval_notes = notes

        # 根据审批状态设置审批人
        if approval_status == ApprovalStatus.APPROVED:
            if ticket.approval_status == ApprovalStatus.PENDING_MANAGER:
                ticket.approved_by_manager_id = approver_id
            elif ticket.approval_status == ApprovalStatus.PENDING_FINANCE:
                ticket.approved_by_finance_id = approver_id

        self.session.add(ticket)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def assign_to_admin(
        self,
        ticket_id: int,
        admin_id: int
    ) -> Optional[Ticket]:
        """
        将工单分配给行政人员

        Args:
            ticket_id: 工单ID
            admin_id: 行政人员ID

        Returns:
            更新后的工单或None
        """
        ticket = self.get_by_id(ticket_id)
        if not ticket:
            return None

        ticket.assigned_admin_id = admin_id
        ticket.processing_status = ProcessingStatus.IN_PROGRESS

        self.session.add(ticket)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def close_ticket(
        self,
        ticket_id: int,
        actual_cost: Optional[float] = None
    ) -> Optional[Ticket]:
        """
        关闭工单

        Args:
            ticket_id: 工单ID
            actual_cost: 实际费用

        Returns:
            更新后的工单或None
        """
        ticket = self.get_by_id(ticket_id)
        if not ticket:
            return None

        ticket.processing_status = ProcessingStatus.COMPLETED
        ticket.closed_at = datetime.utcnow()
        if actual_cost is not None:
            ticket.actual_cost = actual_cost

        self.session.add(ticket)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

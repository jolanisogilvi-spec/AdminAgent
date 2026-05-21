from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, Text
from sqlmodel import Field, SQLModel

from .enums import ApprovalStatus, ProcessingStatus, TicketType, UrgencyLevel


class Ticket(SQLModel, table=True):
    __tablename__ = "tickets"

    id: Optional[int] = Field(default=None, primary_key=True)
    requester_id: int = Field(foreign_key="users.id", index=True)
    original_text: str = Field(sa_column=Column(Text))
    attachments: Optional[str] = Field(default=None, sa_column=Column(Text))
    ticket_type: TicketType
    related_asset_id: Optional[int] = Field(default=None, foreign_key="assets.id")
    estimated_cost: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    approval_status: ApprovalStatus = Field(default=ApprovalStatus.NO_APPROVAL)
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING, index=True)
    assigned_to: Optional[int] = Field(default=None, foreign_key="users.id")
    urgency: UrgencyLevel = Field(default=UrgencyLevel.NORMAL)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = Field(default=None)

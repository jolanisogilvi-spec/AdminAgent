from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import ApprovalStatus, ProcessingStatus, TicketType, UrgencyLevel


class TicketBase(BaseModel):
    original_text: str = Field(..., min_length=1)
    attachments: Optional[str] = None
    ticket_type: TicketType
    related_asset_id: Optional[int] = None
    estimated_cost: float = Field(0, ge=0)
    urgency: UrgencyLevel = UrgencyLevel.NORMAL


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    original_text: Optional[str] = None
    attachments: Optional[str] = None
    ticket_type: Optional[TicketType] = None
    related_asset_id: Optional[int] = None
    estimated_cost: Optional[float] = Field(None, ge=0)
    approval_status: Optional[ApprovalStatus] = None
    processing_status: Optional[ProcessingStatus] = None
    assigned_to: Optional[int] = None
    urgency: Optional[UrgencyLevel] = None


class TicketResponse(TicketBase):
    id: int
    requester_id: int
    approval_status: ApprovalStatus
    processing_status: ProcessingStatus
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True

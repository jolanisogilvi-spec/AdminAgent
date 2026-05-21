from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import ApprovalStatus


class ApprovalRecordBase(BaseModel):
    comment: Optional[str] = Field(None, description="Approval comment")


class ApprovalRecordCreate(ApprovalRecordBase):
    ticket_id: int
    approval_type: str


class ApprovalRecordUpdate(BaseModel):
    status: Optional[ApprovalStatus] = None
    comment: Optional[str] = None


class ApprovalRecordResponse(ApprovalRecordBase):
    id: int
    ticket_id: int
    approver_id: int
    approval_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

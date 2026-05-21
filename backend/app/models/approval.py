from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class ApprovalRecord(SQLModel, table=True):
    __tablename__ = "approval_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="tickets.id", index=True)
    approver_id: int = Field(foreign_key="users.id")
    approval_type: str = Field(max_length=50)
    status: str = Field(max_length=20)
    comment: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)

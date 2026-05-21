from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from .enums import TaskStatus


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    related_ticket_id: Optional[int] = Field(default=None, foreign_key="tickets.id")
    assigned_to: int = Field(foreign_key="users.id", index=True)
    status: TaskStatus = Field(default=TaskStatus.TODO, index=True)
    priority: int = Field(default=0)
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

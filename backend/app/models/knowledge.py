from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class KnowledgeBase(SQLModel, table=True):
    __tablename__ = "knowledge_base"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    content: str = Field(sa_column=Column(Text))
    category: str = Field(max_length=50, index=True)
    embedding: Optional[str] = Field(default=None, sa_column=Column(Text))
    view_count: int = Field(default=0)
    is_active: bool = Field(default=True, index=True)
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from .enums import UserRole


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    full_name: str = Field(max_length=100)
    password_hash: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.EMPLOYEE)
    department: str = Field(max_length=100)
    email: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

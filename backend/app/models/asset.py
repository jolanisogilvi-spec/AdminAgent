from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, Text
from sqlmodel import Field, SQLModel

from .enums import AssetCategory, AssetStatus


class Asset(SQLModel, table=True):
    __tablename__ = "assets"

    id: Optional[int] = Field(default=None, primary_key=True)
    asset_code: str = Field(unique=True, index=True, max_length=50)
    name: str = Field(max_length=200)
    category: AssetCategory
    status: AssetStatus = Field(default=AssetStatus.IDLE, index=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")
    current_stock: int = Field(default=0)
    unit_price: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10, 2), nullable=True),
    )
    purchase_date: Optional[date] = Field(default=None)
    warranty_expire: Optional[date] = Field(default=None)
    location: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

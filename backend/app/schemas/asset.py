from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import AssetCategory, AssetStatus


class AssetBase(BaseModel):
    asset_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    category: AssetCategory
    status: AssetStatus = AssetStatus.IDLE
    owner_id: Optional[int] = None
    current_stock: int = Field(0, ge=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    purchase_date: Optional[date] = None
    warranty_expire: Optional[date] = None
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[AssetCategory] = None
    status: Optional[AssetStatus] = None
    owner_id: Optional[int] = None
    current_stock: Optional[int] = Field(None, ge=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    purchase_date: Optional[date] = None
    warranty_expire: Optional[date] = None
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class AssetStockUpdate(BaseModel):
    quantity_change: int


class AssetAssign(BaseModel):
    user_id: int


class AssetResponse(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    total: int
    items: list[AssetResponse]
    skip: int
    limit: int


class AssetStatistics(BaseModel):
    total_count: int
    idle_count: int
    in_use_count: int
    maintenance_count: int
    scrapped_count: int
    total_value: float
    total_stock: int


class AssetCategoryStatistics(BaseModel):
    category: AssetCategory
    statistics: AssetStatistics

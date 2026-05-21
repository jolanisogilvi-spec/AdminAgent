from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.core.database import get_session
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from app.services.asset_service import AssetService

router = APIRouter(tags=["资产管理"])

@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset_data: AssetCreate,
    session: Session = Depends(get_session),
):
    """创建资产"""
    # 检查资产编号是否已存在
    existing = AssetService.get_asset_by_code(session, asset_data.asset_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="资产编号已存在"
        )

    asset = AssetService.create_asset(session, asset_data)
    return asset

@router.get("/", response_model=List[AssetResponse])
def get_assets(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    status: str = None,
    session: Session = Depends(get_session),
):
    """获取资产列表"""
    assets = AssetService.get_assets(
        session, skip=skip, limit=limit, category=category, status=status
    )
    return assets

@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, session: Session = Depends(get_session)):
    """获取单个资产"""
    asset = AssetService.get_asset(session, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="资产不存在"
        )
    return asset

@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    session: Session = Depends(get_session),
):
    """更新资产"""
    asset = AssetService.update_asset(session, asset_id, asset_data)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="资产不存在"
        )
    return asset

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, session: Session = Depends(get_session)):
    """删除资产"""
    success = AssetService.delete_asset(session, asset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="资产不存在"
        )
    return None

@router.post("/{asset_id}/stock", response_model=AssetResponse)
def update_stock(
    asset_id: int,
    quantity: int,
    session: Session = Depends(get_session),
):
    """更新库存"""
    asset = AssetService.update_stock(session, asset_id, quantity)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="资产不存在"
        )
    return asset

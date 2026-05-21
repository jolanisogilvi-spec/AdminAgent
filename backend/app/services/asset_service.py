from typing import List, Optional
from sqlmodel import Session, select
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate

class AssetService:
    @staticmethod
    def create_asset(session: Session, asset_data: AssetCreate) -> Asset:
        """创建资产"""
        asset = Asset(**asset_data.model_dump())
        session.add(asset)
        session.commit()
        session.refresh(asset)
        return asset

    @staticmethod
    def get_asset(session: Session, asset_id: int) -> Optional[Asset]:
        """获取单个资产"""
        return session.get(Asset, asset_id)

    @staticmethod
    def get_asset_by_code(session: Session, asset_code: str) -> Optional[Asset]:
        """根据资产编号获取资产"""
        statement = select(Asset).where(Asset.asset_code == asset_code)
        return session.exec(statement).first()

    @staticmethod
    def get_assets(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Asset]:
        """获取资产列表"""
        statement = select(Asset)

        if category:
            statement = statement.where(Asset.category == category)

        if status:
            statement = statement.where(Asset.status == status)

        statement = statement.offset(skip).limit(limit)
        results = session.exec(statement)
        return results.all()

    @staticmethod
    def update_asset(
        session: Session, asset_id: int, asset_data: AssetUpdate
    ) -> Optional[Asset]:
        """更新资产"""
        asset = session.get(Asset, asset_id)
        if not asset:
            return None

        update_data = asset_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(asset, key, value)

        session.add(asset)
        session.commit()
        session.refresh(asset)
        return asset

    @staticmethod
    def delete_asset(session: Session, asset_id: int) -> bool:
        """删除资产"""
        asset = session.get(Asset, asset_id)
        if not asset:
            return False

        session.delete(asset)
        session.commit()
        return True

    @staticmethod
    def update_stock(session: Session, asset_id: int, quantity: int) -> Optional[Asset]:
        """更新库存"""
        asset = session.get(Asset, asset_id)
        if not asset:
            return None

        asset.current_stock += quantity
        session.add(asset)
        session.commit()
        session.refresh(asset)
        return asset

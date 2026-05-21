"""Asset Repository - 资产数据访问层

提供资产相关的数据库操作
"""

from typing import List, Optional
from sqlmodel import Session, select, and_, or_
from datetime import datetime

from app.models import Asset, AssetCategory, AssetStatus
from .base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    """资产Repository"""

    def __init__(self, session: Session):
        super().__init__(Asset, session)

    def get_by_code(self, asset_code: str) -> Optional[Asset]:
        """
        根据资产编号获取资产

        Args:
            asset_code: 资产编号

        Returns:
            资产实例或None
        """
        statement = select(Asset).where(Asset.asset_code == asset_code)
        return self.session.exec(statement).first()

    def get_by_category(
        self,
        category: AssetCategory,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        根据分类获取资产

        Args:
            category: 资产分类
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            资产列表
        """
        statement = (
            select(Asset)
            .where(Asset.category == category)
            .order_by(Asset.asset_name)
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def get_by_status(
        self,
        status: AssetStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        根据状态获取资产

        Args:
            status: 资产状态
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            资产列表
        """
        statement = (
            select(Asset)
            .where(Asset.status == status)
            .order_by(Asset.asset_name)
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def get_by_owner(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        获取指定用户拥有的资产

        Args:
            owner_id: 归属人ID
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            资产列表
        """
        statement = (
            select(Asset)
            .where(Asset.owner_id == owner_id)
            .order_by(Asset.asset_name)
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def get_idle_assets(
        self,
        category: Optional[AssetCategory] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        获取闲置资产

        Args:
            category: 资产分类（可选）
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            资产列表
        """
        statement = select(Asset).where(Asset.status == AssetStatus.IDLE)

        if category:
            statement = statement.where(Asset.category == category)

        statement = (
            statement
            .order_by(Asset.asset_name)
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def get_low_stock_assets(
        self,
        threshold: int = 10,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        获取库存不足的资产

        Args:
            threshold: 库存阈值
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            资产列表
        """
        statement = (
            select(Asset)
            .where(Asset.current_stock <= threshold)
            .where(Asset.category == AssetCategory.CONSUMABLES)  # 通常只关注耗材库存
            .order_by(Asset.current_stock)
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def get_expiring_warranty(
        self,
        days: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        获取保修期即将到期的资产

        Args:
            days: 提前天数
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            资产列表
        """
        from datetime import timedelta
        expiry_date = datetime.utcnow() + timedelta(days=days)

        statement = (
            select(Asset)
            .where(Asset.warranty_until.isnot(None))
            .where(Asset.warranty_until <= expiry_date)
            .where(Asset.warranty_until >= datetime.utcnow())
            .order_by(Asset.warranty_until)
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def search(
        self,
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        搜索资产（名称、编号、品牌、型号）

        Args:
            keyword: 搜索关键词
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            资产列表
        """
        search_pattern = f"%{keyword}%"
        statement = (
            select(Asset)
            .where(
                or_(
                    Asset.asset_name.ilike(search_pattern),
                    Asset.asset_code.ilike(search_pattern),
                    Asset.brand.ilike(search_pattern),
                    Asset.model.ilike(search_pattern)
                )
            )
            .order_by(Asset.asset_name)
            .offset(skip)
            .limit(limit)
        )
        results = self.session.exec(statement)
        return results.all()

    def update_stock(
        self,
        asset_id: int,
        quantity_change: int
    ) -> Optional[Asset]:
        """
        更新资产库存

        Args:
            asset_id: 资产ID
            quantity_change: 库存变化量（正数为增加，负数为减少）

        Returns:
            更新后的资产或None
        """
        asset = self.get_by_id(asset_id)
        if not asset:
            return None

        new_stock = asset.current_stock + quantity_change
        if new_stock < 0:
            raise ValueError(f"库存不足，当前库存：{asset.current_stock}，需要：{abs(quantity_change)}")

        asset.current_stock = new_stock

        # 自动更新状态
        if new_stock == 0 and asset.category == AssetCategory.CONSUMABLES:
            asset.status = AssetStatus.IDLE  # 耗材库存为0时标记为闲置（需要采购）

        self.session.add(asset)
        self.session.commit()
        self.session.refresh(asset)
        return asset

    def assign_to_user(
        self,
        asset_id: int,
        user_id: int
    ) -> Optional[Asset]:
        """
        将资产分配给用户

        Args:
            asset_id: 资产ID
            user_id: 用户ID

        Returns:
            更新后的资产或None
        """
        asset = self.get_by_id(asset_id)
        if not asset:
            return None

        if asset.status != AssetStatus.IDLE:
            raise ValueError(f"资产状态为{asset.status.value}，无法分配")

        asset.owner_id = user_id
        asset.status = AssetStatus.IN_USE

        self.session.add(asset)
        self.session.commit()
        self.session.refresh(asset)
        return asset

    def return_asset(
        self,
        asset_id: int
    ) -> Optional[Asset]:
        """
        归还资产

        Args:
            asset_id: 资产ID

        Returns:
            更新后的资产或None
        """
        asset = self.get_by_id(asset_id)
        if not asset:
            return None

        asset.owner_id = None
        asset.status = AssetStatus.IDLE

        self.session.add(asset)
        self.session.commit()
        self.session.refresh(asset)
        return asset

    def mark_under_repair(
        self,
        asset_id: int
    ) -> Optional[Asset]:
        """
        标记资产为维修中

        Args:
            asset_id: 资产ID

        Returns:
            更新后的资产或None
        """
        asset = self.get_by_id(asset_id)
        if not asset:
            return None

        asset.status = AssetStatus.UNDER_REPAIR

        self.session.add(asset)
        self.session.commit()
        self.session.refresh(asset)
        return asset

    def get_statistics_by_category(self) -> dict:
        """
        获取按分类统计的资产信息

        Returns:
            统计数据字典
        """
        all_assets = self.get_all(limit=10000)  # 获取所有资产

        stats = {}
        for category in AssetCategory:
            category_assets = [a for a in all_assets if a.category == category]

            stats[category.value] = {
                "total_count": len(category_assets),
                "idle_count": sum(1 for a in category_assets if a.status == AssetStatus.IDLE),
                "in_use_count": sum(1 for a in category_assets if a.status == AssetStatus.IN_USE),
                "under_repair_count": sum(1 for a in category_assets if a.status == AssetStatus.UNDER_REPAIR),
                "scrapped_count": sum(1 for a in category_assets if a.status == AssetStatus.SCRAPPED),
                "total_value": sum(a.unit_price or 0 for a in category_assets),
                "total_stock": sum(a.current_stock for a in category_assets)
            }

        return stats

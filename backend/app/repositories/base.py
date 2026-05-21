"""Base Repository 基类

提供通用的CRUD操作，所有具体的Repository继承此类
"""

from typing import Generic, TypeVar, Type, Optional, List
from sqlmodel import Session, select, func
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """通用Repository基类"""

    def __init__(self, model: Type[ModelType], session: Session):
        """
        初始化Repository

        Args:
            model: SQLModel模型类
            session: 数据库会话
        """
        self.model = model
        self.session = session

    def create(self, obj: ModelType) -> ModelType:
        """
        创建新记录

        Args:
            obj: 模型实例

        Returns:
            创建的模型实例（包含ID）
        """
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        根据ID获取记录

        Args:
            id: 记录ID

        Returns:
            模型实例或None
        """
        return self.session.get(self.model, id)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        获取所有记录（分页）

        Args:
            skip: 跳过的记录数
            limit: 返回的最大记录数
            order_by: 排序字段

        Returns:
            模型实例列表
        """
        statement = select(self.model).offset(skip).limit(limit)

        if order_by:
            # 简单的排序支持，生产环境需要更复杂的实现
            if order_by.startswith("-"):
                field = order_by[1:]
                statement = statement.order_by(getattr(self.model, field).desc())
            else:
                statement = statement.order_by(getattr(self.model, order_by))

        results = self.session.exec(statement)
        return results.all()

    def update(self, id: int, obj_data: dict) -> Optional[ModelType]:
        """
        更新记录

        Args:
            id: 记录ID
            obj_data: 要更新的字段字典

        Returns:
            更新后的模型实例或None
        """
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None

        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        """
        删除记录

        Args:
            id: 记录ID

        Returns:
            是否删除成功
        """
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False

        self.session.delete(db_obj)
        self.session.commit()
        return True

    def count(self) -> int:
        """
        获取记录总数

        Returns:
            记录总数
        """
        statement = select(func.count()).select_from(self.model)
        return self.session.exec(statement).one()

    def exists(self, id: int) -> bool:
        """
        检查记录是否存在

        Args:
            id: 记录ID

        Returns:
            是否存在
        """
        return self.get_by_id(id) is not None

"""数据模型模块"""

from .enums import (
    UserRole,
    TicketType,
    ApprovalStatus,
    ProcessingStatus,
    UrgencyLevel,
    AssetCategory,
    AssetStatus,
    TaskStatus,
)
from .user import User
from .ticket import Ticket
from .asset import Asset
from .task import Task
from .knowledge import KnowledgeBase
from .config import SysConfig, ConfigKeys
from .approval import ApprovalRecord

__all__ = [
    # Enums
    "UserRole",
    "TicketType",
    "ApprovalStatus",
    "ProcessingStatus",
    "UrgencyLevel",
    "AssetCategory",
    "AssetStatus",
    "TaskStatus",
    # Models
    "User",
    "Ticket",
    "Asset",
    "Task",
    "KnowledgeBase",
    "SysConfig",
    "ConfigKeys",
    "ApprovalRecord",
]

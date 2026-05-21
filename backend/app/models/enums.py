from enum import Enum


class UserRole(str, Enum):
    EMPLOYEE = "employee"
    ADMIN_STAFF = "admin_staff"
    MANAGER = "manager"
    SYS_ADMIN = "sys_admin"


class TicketType(str, Enum):
    PURCHASE = "purchase"
    REPAIR = "repair"
    REQUISITION = "requisition"
    CONSULTATION = "consultation"


class ApprovalStatus(str, Enum):
    NO_APPROVAL = "no_approval"
    PENDING_MANAGER = "pending_manager"
    PENDING_FINANCE = "pending_finance"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"


class UrgencyLevel(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AssetCategory(str, Enum):
    IT_EQUIPMENT = "it_equipment"
    OFFICE_FURNITURE = "office_furniture"
    CONSUMABLES = "consumables"
    OTHER = "other"


class AssetStatus(str, Enum):
    IDLE = "idle"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    SCRAPPED = "scrapped"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

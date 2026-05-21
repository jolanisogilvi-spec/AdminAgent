from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import TaskStatus


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    related_ticket_id: Optional[int] = None
    assigned_to: int
    status: TaskStatus = TaskStatus.TODO
    priority: int = 0
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    related_ticket_id: Optional[int] = None
    assigned_to: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskStart(BaseModel):
    notes: Optional[str] = None


class TaskComplete(BaseModel):
    notes: Optional[str] = None


class TaskProgressUpdate(BaseModel):
    progress_percentage: int = Field(..., ge=0, le=100)
    notes: Optional[str] = None


class TaskCancel(BaseModel):
    reason: Optional[str] = None


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    total: int
    items: list[TaskResponse]
    skip: int
    limit: int


class TaskKanbanResponse(BaseModel):
    todo: list[TaskResponse]
    in_progress: list[TaskResponse]
    completed: list[TaskResponse]
    cancelled: list[TaskResponse]


class TaskStatistics(BaseModel):
    total_tasks: int
    status_counts: dict
    completion_rate: float
    overdue_count: int

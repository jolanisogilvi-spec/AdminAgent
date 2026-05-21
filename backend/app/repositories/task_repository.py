"""Task Repository - 任务数据访问层

提供任务相关的数据库操作
"""

from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta

from app.models import Task, TaskStatus
from .base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """任务Repository"""

    def __init__(self, session: Session):
        super().__init__(Task, session)

    def get_by_ticket(
        self,
        ticket_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """获取指定工单的所有任务"""
        statement = (
            select(Task)
            .where(Task.related_ticket_id == ticket_id)
            .order_by(Task.created_at)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_by_assignee(
        self,
        assignee_id: int,
        status: Optional[TaskStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """获取分配给指定用户的任务"""
        statement = select(Task).where(Task.assigned_to == assignee_id)

        if status:
            statement = statement.where(Task.status == status)

        statement = (
            statement
            .order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_by_status(
        self,
        status: TaskStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """根据状态获取任务"""
        statement = (
            select(Task)
            .where(Task.status == status)
            .order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_overdue_tasks(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """获取逾期的任务"""
        now = datetime.utcnow()
        statement = (
            select(Task)
            .where(Task.due_date.isnot(None))
            .where(Task.due_date < now)
            .where(Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]))
            .order_by(Task.due_date)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_upcoming_tasks(
        self,
        days: int = 3,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """获取即将到期的任务"""
        now = datetime.utcnow()
        upcoming_date = now + timedelta(days=days)

        statement = (
            select(Task)
            .where(Task.due_date.isnot(None))
            .where(Task.due_date >= now)
            .where(Task.due_date <= upcoming_date)
            .where(Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]))
            .order_by(Task.due_date)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_kanban_tasks(
        self,
        assignee_id: Optional[int] = None
    ) -> dict:
        """获取看板视图的任务（按状态分组）"""
        statement = select(Task)

        if assignee_id:
            statement = statement.where(Task.assigned_to == assignee_id)

        tasks = self.session.exec(statement).all()

        kanban = {
            TaskStatus.TODO.value: [],
            TaskStatus.IN_PROGRESS.value: [],
            TaskStatus.COMPLETED.value: [],
            TaskStatus.CANCELLED.value: []
        }

        for task in tasks:
            kanban[task.status.value].append(task)

        kanban[TaskStatus.TODO.value].sort(
            key=lambda t: (t.due_date or datetime.max, t.created_at)
        )
        kanban[TaskStatus.IN_PROGRESS.value].sort(
            key=lambda t: (t.due_date or datetime.max, t.created_at)
        )
        kanban[TaskStatus.COMPLETED.value].sort(
            key=lambda t: t.completed_at or t.updated_at,
            reverse=True
        )

        return kanban

    def start_task(self, task_id: int) -> Optional[Task]:
        """开始任务"""
        task = self.get_by_id(task_id)
        if not task:
            return None

        if task.status != TaskStatus.TODO:
            raise ValueError(f"任务状态为{task.status.value}，无法开始")

        task.status = TaskStatus.IN_PROGRESS
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def complete_task(self, task_id: int) -> Optional[Task]:
        """完成任务"""
        task = self.get_by_id(task_id)
        if not task:
            return None

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def cancel_task(self, task_id: int) -> Optional[Task]:
        """取消任务"""
        task = self.get_by_id(task_id)
        if not task:
            return None

        task.status = TaskStatus.CANCELLED
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_statistics_by_assignee(
        self,
        assignee_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """获取指定负责人的任务统计"""
        statement = select(Task).where(Task.assigned_to == assignee_id)

        if start_date:
            statement = statement.where(Task.created_at >= start_date)
        if end_date:
            statement = statement.where(Task.created_at <= end_date)

        tasks = self.session.exec(statement).all()

        status_counts = {
            status.value: sum(1 for t in tasks if t.status == status)
            for status in TaskStatus
        }

        total_tasks = len(tasks)
        completed_tasks = status_counts[TaskStatus.COMPLETED.value]
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        completed_with_time = [
            t for t in tasks
            if t.status == TaskStatus.COMPLETED and t.completed_at
        ]
        avg_completion_time = None
        if completed_with_time:
            total_time = sum(
                (t.completed_at - t.created_at).total_seconds()
                for t in completed_with_time
            )
            avg_completion_time = total_time / len(completed_with_time) / 3600

        now = datetime.utcnow()
        overdue_count = sum(
            1 for t in tasks
            if t.due_date and t.due_date < now
            and t.status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]
        )

        return {
            "total_tasks": total_tasks,
            "status_counts": status_counts,
            "completion_rate": round(completion_rate, 2),
            "avg_completion_time_hours": avg_completion_time,
            "overdue_count": overdue_count,
        }

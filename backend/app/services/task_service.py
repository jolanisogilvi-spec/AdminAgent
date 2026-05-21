from typing import List, Optional
from sqlmodel import Session, select
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

class TaskService:
    @staticmethod
    def create_task(session: Session, task_data: TaskCreate) -> Task:
        """创建任务"""
        task = Task(**task_data.model_dump())
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def get_task(session: Session, task_id: int) -> Optional[Task]:
        """获取单个任务"""
        return session.get(Task, task_id)

    @staticmethod
    def get_tasks(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        ticket_id: Optional[int] = None,
        assigned_to: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Task]:
        """获取任务列表"""
        statement = select(Task)

        if ticket_id:
            statement = statement.where(Task.related_ticket_id == ticket_id)

        if assigned_to:
            statement = statement.where(Task.assigned_to == assigned_to)

        if status:
            statement = statement.where(Task.status == status)

        statement = statement.offset(skip).limit(limit)
        results = session.exec(statement)
        return results.all()

    @staticmethod
    def update_task(
        session: Session, task_id: int, task_data: TaskUpdate
    ) -> Optional[Task]:
        """更新任务"""
        task = session.get(Task, task_id)
        if not task:
            return None

        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)

        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def delete_task(session: Session, task_id: int) -> bool:
        """删除任务"""
        task = session.get(Task, task_id)
        if not task:
            return False

        session.delete(task)
        session.commit()
        return True

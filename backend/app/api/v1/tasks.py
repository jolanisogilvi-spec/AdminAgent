from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.core.database import get_session
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import TaskService

router = APIRouter(tags=["任务管理"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
):
    """创建任务"""
    task = TaskService.create_task(session, task_data)
    return task

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    related_ticket_id: int = None,
    assigned_to: int = None,
    status: str = None,
    session: Session = Depends(get_session),
):
    """获取任务列表"""
    tasks = TaskService.get_tasks(
        session,
        skip=skip,
        limit=limit,
        ticket_id=related_ticket_id,
        assigned_to=assigned_to,
        status=status,
    )
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, session: Session = Depends(get_session)):
    """获取单个任务"""
    task = TaskService.get_task(session, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在"
        )
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
):
    """更新任务"""
    task = TaskService.update_task(session, task_id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在"
        )
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    """删除任务"""
    success = TaskService.delete_task(session, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在"
        )
    return None

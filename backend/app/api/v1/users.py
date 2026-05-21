from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_password_hash
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(tags=["Users"])


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: UserRole = UserRole.EMPLOYEE
    department: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: UserRole
    department: str
    email: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[UserResponse])
def list_users(
    role: Optional[UserRole] = None,
    keyword: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    statement = select(User)
    if role:
        statement = statement.where(User.role == role)
    if keyword:
        like_keyword = f"%{keyword}%"
        statement = statement.where(
            (User.username.like(like_keyword))
            | (User.full_name.like(like_keyword))
            | (User.department.like(like_keyword))
        )
    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    user = User(
        username=data.username,
        full_name=data.full_name,
        password_hash=get_password_hash(data.password),
        role=data.role,
        department=data.department,
        email=data.email,
        phone=data.phone,
        is_active=data.is_active,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)
    password = update_data.pop("password", None)
    for key, value in update_data.items():
        setattr(user, key, value)
    if password:
        user.password_hash = get_password_hash(password)
    user.updated_at = datetime.utcnow()

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    session.delete(user)
    session.commit()

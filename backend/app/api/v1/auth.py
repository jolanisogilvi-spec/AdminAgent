from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.database import get_session
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(LoginRequest):
    name: str
    department: str
    role: UserRole = UserRole.EMPLOYEE


def serialize_user(user: User) -> dict:
    return {
        "id": str(user.id),
        "username": user.username,
        "name": user.full_name,
        "role": user.role.value,
        "department": user.department,
        "createdAt": user.created_at.isoformat(),
    }


def ensure_seed_user(session: Session) -> None:
    existing = session.exec(select(User).where(User.username == settings.ADMIN_INITIAL_USERNAME)).first()
    if existing:
        return

    user = User(
        username=settings.ADMIN_INITIAL_USERNAME,
        full_name="系统管理员",
        password_hash=get_password_hash(settings.ADMIN_INITIAL_PASSWORD),
        role=UserRole.SYS_ADMIN,
        department="系统管理",
        email="admin@example.com",
    )
    session.add(user)
    session.commit()


@router.post("/login")
def login(data: LoginRequest, session: Session = Depends(get_session)):
    ensure_seed_user(session)
    user = session.exec(select(User).where(User.username == data.username)).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": user.username}, expires)
    return {"token": token, "user": serialize_user(user)}


@router.post("/register")
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    user = User(
        username=data.username,
        full_name=data.name,
        password_hash=get_password_hash(data.password),
        role=data.role,
        department=data.department,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token({"sub": user.username})
    return {"token": token, "user": serialize_user(user)}


@router.get("/me")
def me(current_user: User = Depends(get_current_active_user)):
    return serialize_user(current_user)


@router.post("/logout")
def logout():
    return {"message": "ok"}

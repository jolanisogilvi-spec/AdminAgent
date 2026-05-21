from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class ConfigKeys:
    LLM_BASE_URL = "LLM_BASE_URL"
    LLM_API_KEY = "LLM_API_KEY"
    LLM_MODEL_NAME = "LLM_MODEL"
    LLM_TEMPERATURE = "LLM_TEMPERATURE"
    LLM_MAX_TOKENS = "LLM_MAX_TOKENS"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    EMBEDDING_BASE_URL = "EMBEDDING_BASE_URL"
    EMBEDDING_MODEL = "EMBEDDING_MODEL"
    VECTOR_DB_PATH = "VECTOR_DB_PATH"
    APPROVAL_THRESHOLD_AMOUNT = "APPROVAL_THRESHOLD"
    AUTO_ASSIGN_ADMIN = "AUTO_ASSIGN_ADMIN"
    SYSTEM_NAME = "SYSTEM_NAME"
    SESSION_TIMEOUT = "SESSION_TIMEOUT"
    MAX_UPLOAD_SIZE = "MAX_UPLOAD_SIZE"


class SysConfig(SQLModel, table=True):
    __tablename__ = "sys_config"

    id: Optional[int] = Field(default=None, primary_key=True)
    config_key: str = Field(unique=True, index=True, max_length=100)
    config_value: str = Field(sa_column=Column(Text))
    description: Optional[str] = Field(default=None, max_length=500)
    is_sensitive: bool = Field(default=False)
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_at: datetime = Field(default_factory=datetime.utcnow)

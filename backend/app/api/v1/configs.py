from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from app.core.database import get_session
from app.core.redis import RedisClient, get_redis
from app.services.config_service import ConfigService

router = APIRouter()


class ConfigCreate(BaseModel):
    config_key: str
    config_value: str
    description: Optional[str] = None
    is_sensitive: bool = False


class ConfigUpdate(BaseModel):
    config_value: str
    description: Optional[str] = None
    is_sensitive: Optional[bool] = None


class ConfigResponse(BaseModel):
    id: int
    config_key: str
    config_value: str
    description: Optional[str]
    is_sensitive: bool
    updated_at: datetime

    class Config:
        from_attributes = True


def get_config_service(
    db: Session = Depends(get_session),
    redis: RedisClient = Depends(get_redis),
) -> ConfigService:
    return ConfigService(db, redis)


@router.post("/", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(config_data: ConfigCreate, service: ConfigService = Depends(get_config_service)):
    return await service.set_config(
        config_key=config_data.config_key,
        config_value=config_data.config_value,
        description=config_data.description,
        is_sensitive=config_data.is_sensitive,
        updated_by=1,
    )


@router.get("/{config_key}")
async def get_config(config_key: str, service: ConfigService = Depends(get_config_service)):
    value = await service.get_config(config_key)
    if value is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    return {"config_key": config_key, "config_value": value}


@router.get("/", response_model=list[ConfigResponse])
async def list_configs(
    include_sensitive: bool = False,
    service: ConfigService = Depends(get_config_service),
):
    return service.list_configs(include_sensitive=include_sensitive)


@router.put("/{config_key}", response_model=ConfigResponse)
async def update_config(
    config_key: str,
    config_data: ConfigUpdate,
    service: ConfigService = Depends(get_config_service),
):
    return await service.set_config(
        config_key=config_key,
        config_value=config_data.config_value,
        description=config_data.description,
        is_sensitive=config_data.is_sensitive,
        updated_by=1,
    )


@router.delete("/{config_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(config_key: str, service: ConfigService = Depends(get_config_service)):
    if not await service.delete_config(config_key):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")


@router.post("/init")
async def init_default_configs(service: ConfigService = Depends(get_config_service)):
    await service.init_default_configs()
    return {"message": "Default configs initialized"}

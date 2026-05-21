import logging
from typing import Dict, List, Optional

from sqlmodel import Session, select

from app.core.redis import RedisClient
from app.models import SysConfig

logger = logging.getLogger(__name__)


class ConfigService:
    """Manage runtime configuration values with a short-lived cache."""

    def __init__(self, db: Session, redis: RedisClient):
        self.db = db
        self.redis = redis
        self.cache_prefix = "sys_config:"

    async def get_config(self, config_key: str) -> Optional[str]:
        cache_key = f"{self.cache_prefix}{config_key}"
        cached_value = await self.redis.get(cache_key)
        if cached_value:
            return cached_value

        stmt = select(SysConfig).where(SysConfig.config_key == config_key)
        config = self.db.exec(stmt).first()

        if config:
            await self.redis.set(cache_key, config.config_value, expire=300)
            return config.config_value

        return None

    async def get_configs(self, keys: List[str]) -> Dict[str, str]:
        result = {}
        for key in keys:
            value = await self.get_config(key)
            if value:
                result[key] = value
        return result

    async def set_config(
        self,
        config_key: str,
        config_value: str,
        description: Optional[str] = None,
        is_sensitive: Optional[bool] = None,
        updated_by: Optional[int] = None,
    ) -> SysConfig:
        try:
            stmt = select(SysConfig).where(SysConfig.config_key == config_key)
            config = self.db.exec(stmt).first()

            if config:
                config.config_value = config_value
                if description is not None:
                    config.description = description
                if is_sensitive is not None:
                    config.is_sensitive = is_sensitive
                config.updated_by = updated_by
            else:
                config = SysConfig(
                    config_key=config_key,
                    config_value=config_value,
                    description=description,
                    is_sensitive=bool(is_sensitive),
                    updated_by=updated_by,
                )

            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)

            cache_key = f"{self.cache_prefix}{config_key}"
            await self.redis.set(cache_key, config_value, expire=300)
            await self.redis.delete(f"{self.cache_prefix}llm")

            logger.info("Set config: %s", config_key)
            return config

        except Exception as exc:
            logger.error("Failed to set config %s: %s", config_key, exc)
            self.db.rollback()
            raise

    def list_configs(self, include_sensitive: bool = False) -> List[SysConfig]:
        stmt = select(SysConfig)
        if not include_sensitive:
            stmt = stmt.where(SysConfig.is_sensitive == False)

        return list(self.db.exec(stmt).all())

    async def delete_config(self, config_key: str) -> bool:
        stmt = select(SysConfig).where(SysConfig.config_key == config_key)
        config = self.db.exec(stmt).first()

        if not config:
            return False

        try:
            self.db.delete(config)
            self.db.commit()

            cache_key = f"{self.cache_prefix}{config_key}"
            await self.redis.delete(cache_key)
            await self.redis.delete(f"{self.cache_prefix}llm")

            logger.info("Deleted config: %s", config_key)
            return True

        except Exception as exc:
            logger.error("Failed to delete config %s: %s", config_key, exc)
            self.db.rollback()
            return False

    async def init_default_configs(self) -> None:
        default_configs = [
            {
                "config_key": "SYSTEM_NAME",
                "config_value": "Admin Agent",
                "description": "System display name",
                "is_sensitive": False,
            },
            {
                "config_key": "SESSION_TIMEOUT",
                "config_value": "10080",
                "description": "Login session timeout in minutes",
                "is_sensitive": False,
            },
            {
                "config_key": "MAX_UPLOAD_SIZE",
                "config_value": "10",
                "description": "Maximum upload size in MB",
                "is_sensitive": False,
            },
            {
                "config_key": "LLM_BASE_URL",
                "config_value": "https://api.openai.com/v1",
                "description": "LLM API base URL",
                "is_sensitive": False,
            },
            {
                "config_key": "LLM_API_KEY",
                "config_value": "sk-your-api-key",
                "description": "LLM API key",
                "is_sensitive": True,
            },
            {
                "config_key": "LLM_MODEL",
                "config_value": "gpt-4o",
                "description": "LLM model name",
                "is_sensitive": False,
            },
            {
                "config_key": "LLM_TEMPERATURE",
                "config_value": "0.2",
                "description": "LLM response randomness, range 0 to 2",
                "is_sensitive": False,
            },
            {
                "config_key": "LLM_MAX_TOKENS",
                "config_value": "2000",
                "description": "Maximum tokens for one LLM response",
                "is_sensitive": False,
            },
            {
                "config_key": "EMBEDDING_BASE_URL",
                "config_value": "https://api.openai.com/v1",
                "description": "Embedding API base URL",
                "is_sensitive": False,
            },
            {
                "config_key": "EMBEDDING_MODEL",
                "config_value": "text-embedding-3-small",
                "description": "Embedding model for knowledge search",
                "is_sensitive": False,
            },
            {
                "config_key": "VECTOR_DB_PATH",
                "config_value": "./chroma_data",
                "description": "Local vector database path",
                "is_sensitive": False,
            },
            {
                "config_key": "APPROVAL_THRESHOLD",
                "config_value": "1000",
                "description": "Manager approval threshold amount",
                "is_sensitive": False,
            },
            {
                "config_key": "FINANCE_APPROVAL_THRESHOLD",
                "config_value": "5000",
                "description": "Finance approval threshold amount",
                "is_sensitive": False,
            },
            {
                "config_key": "AUTO_ASSIGN_ADMIN",
                "config_value": "true",
                "description": "Whether new tickets are assigned automatically",
                "is_sensitive": False,
            },
        ]

        for config_data in default_configs:
            existing = await self.get_config(config_data["config_key"])
            if not existing:
                await self.set_config(**config_data)

        logger.info("Default configs initialized")

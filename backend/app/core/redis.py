from typing import Optional


class RedisClient:
    """Small async cache facade used by services.

    It keeps the app runnable when Redis is not available locally. The public
    methods match the subset used by this project.
    """

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> None:
        self._store[key] = value

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)


redis_client = RedisClient()


def get_redis() -> RedisClient:
    return redis_client

from typing import Annotated

from fastapi import Depends

from app.core.config import get_settings
from app.infrastructure.redis.manager import RedisManager


def get_redis_manager_infr() -> RedisManager:
    settings = get_settings()
    return RedisManager(settings.REDIS_VOLATILE_URL, settings.REDIS_DURABLE_URL)


def get_cache_client(
    redis_manager: Annotated[RedisManager, Depends(get_redis_manager_infr)],
):
    return redis_manager.cache_client

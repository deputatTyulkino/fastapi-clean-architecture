from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.redis.i_cache_client import ICacheClient
from app.domain.interfaces.redis.i_serializer_services import ISerializerServices
from app.infrastructure.logging.logger import get_logger

T = TypeVar("T")

_fallback_logger: ILogger = get_logger(component="redis_cache")


def redis_cache(key_builder: Callable[..., str], ttl: int, type_: type[T]):
    def wrapper(func: Callable[..., Any]):
        @wraps(func)
        async def inner(*args, **kwargs):
            instance = args[0]
            logger = getattr(instance, "logger", None) or _fallback_logger
            logger = logger.bind(cache_func=func.__qualname__)
            serializer: ISerializerServices | None = getattr(
                instance, "serializer_services", None
            )
            if serializer is None:
                logger.error("cache_serializer_missing")
                raise RuntimeError("Ошибка получения serializer")
            cache_client: ICacheClient | None = getattr(instance, "cache_client", None)
            if cache_client is None:
                logger.error("cache_client_missing")
                raise RuntimeError("Ошибка получения cache client")
            key = key_builder(args, kwargs)
            cache = await cache_client.get(key)
            if cache is not None:
                logger.debug("cache_hit", key=key)
                return serializer.deserializer(cache, type_)
            logger.debug("cache_miss", key=key)
            res = await func(args, kwargs)
            serialized_res = serializer.serializer(res, type_)
            if serialized_res is None:
                logger.error("cache_serialization_failed", key=key)
                raise ValueError("Ошибка сериализации")
            await cache_client.set(key, serialized_res, ttl)
            logger.debug("cache_set", key=key, ttl=ttl)
            return res

        return inner

    return wrapper

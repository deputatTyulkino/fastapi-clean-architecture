from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from app.domain.interfaces.redis.i_cache_client import ICacheClient
from app.domain.interfaces.redis.i_serializer_services import ISerializerServices

T = TypeVar("T")


def redis_cache(key_builder: Callable[..., str], ttl: int, type_: type[T]):
    def wrapper(func: Callable[..., Any]):
        @wraps(func)
        async def inner(*args, **kwargs):
            serializer: ISerializerServices | None = getattr(
                args[0], "serializer_services", None
            )
            if serializer is None:
                raise RuntimeError("Ошибка получения serializer")
            cache_client: ICacheClient | None = getattr(args[0], "cache_client", None)
            if cache_client is None:
                raise RuntimeError("Ошибка получения cache client")
            cache = await cache_client.get(key_builder(args, kwargs))
            if cache is not None:
                return serializer.deserializer(cache, type_)
            res = await func(args, kwargs)
            serialized_res = serializer.serializer(res, type_)
            if serialized_res is None:
                raise ValueError("Ошибка сериализации")
            await cache_client.set(key_builder(args, kwargs), serialized_res, ttl)
            return res

        return inner

    return wrapper

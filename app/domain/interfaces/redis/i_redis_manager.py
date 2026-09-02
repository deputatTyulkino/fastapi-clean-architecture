from abc import ABC, abstractmethod
from enum import Enum


class RedisPoolPurpose(str, Enum):
    CACHE = "cache"
    LIMITER = "limiter"
    STATE = "state"


class IRedisManager(ABC):
    @abstractmethod
    async def init(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def acquire_lock(self, key: str, ttl: int) -> str | None:
        raise NotImplementedError()

    @abstractmethod
    async def release_lock(self, key: str, token: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def mark_product_dirty(self, product_id: int) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def pop_dirty_products(self) -> list[int]:
        raise NotImplementedError()

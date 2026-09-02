from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T")


class ISerializerServices(ABC):
    @staticmethod
    @abstractmethod
    def serializer(value: Any, type_: type[T] | None = None) -> str | None:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def deserializer(value: str | None, type_: type[T] | None = None) -> T | Any:
        raise NotImplementedError()

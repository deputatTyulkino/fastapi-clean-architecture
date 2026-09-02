from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T")


class ISerializerServices(ABC):
    @abstractmethod
    @staticmethod
    def serializer(value: Any, type_: type[T] | None = None) -> str | None:
        raise NotImplementedError()

    @abstractmethod
    @staticmethod
    def deserializer(value: str | None, type_: type[T] | None = None) -> T | Any:
        raise NotImplementedError()

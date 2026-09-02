from typing import Any, TypeVar

import orjson
from pydantic import BaseModel, TypeAdapter

from app.domain.interfaces.redis.i_serializer_services import ISerializerServices

T = TypeVar("T")


class SerializerServices(ISerializerServices):
    @staticmethod
    def serializer(value: Any, type_: type[T] | None = None) -> str | None:
        if value is None:
            return None
        if type_ is not None:
            return TypeAdapter(type_).dump_json(value).decode("utf-8")
        if isinstance(value, BaseModel):
            return value.model_dump_json()
        return orjson.dumps(value).decode("utf-8")

    @staticmethod
    def deserializer(value: str | None, type_: type[T] | None = None) -> T | None:
        if value is None:
            return None
        if type_ is None:
            return orjson.loads(value)
        return TypeAdapter(type_).validate_json(value)

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponseSchema(BaseModel, Generic[T]):
    data: T
    success: bool = True

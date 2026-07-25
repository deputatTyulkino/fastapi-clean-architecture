from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")
K = TypeVar("K")


class SuccessPaginatedResponseSchema(BaseModel, Generic[K]):
    items: list[K]
    total: int
    page: int
    limit: int


class SuccessResponseSchema(BaseModel, Generic[T]):
    data: T
    success: bool = True

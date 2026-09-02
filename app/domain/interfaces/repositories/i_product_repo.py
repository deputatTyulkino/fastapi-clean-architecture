from abc import ABC, abstractmethod
from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from app.domain.models.products import (
    MainProductsDomain,
    ProductDomain,
)


class IProductRepo(ABC):
    @abstractmethod
    async def get_all(
        self, params: dict[str, Any]
    ) -> tuple[list[MainProductsDomain], int, int, int]:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_id(self, id: int) -> ProductDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def exists_by_id(self, id: int) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def exists_by_name(self, name: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_category(self, id: int) -> list[MainProductsDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_seller(self, id: int) -> list[MainProductsDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def get_rating_by_id(self, id: int) -> Decimal:
        raise NotImplementedError()

    @abstractmethod
    async def create(self, product_data: ProductDomain) -> ProductDomain:
        raise NotImplementedError()

    @abstractmethod
    async def update(
        self, id: int, product_data: ProductDomain
    ) -> ProductDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def update_reviews_statistics(self, list_id: list[int]) -> Sequence[int]:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, id: int) -> int | None:
        raise NotImplementedError()

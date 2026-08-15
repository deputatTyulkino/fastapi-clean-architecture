from abc import ABC, abstractmethod

from app.domain.models.sellers import SellerDomain


class ISellerRepo(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> SellerDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def exists_by_id(self, id: int) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_product_id(self, product_id: int) -> SellerDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def create(self, seller_data: SellerDomain) -> SellerDomain:
        raise NotImplementedError()

    @abstractmethod
    async def update(self, id: int, seller_data: SellerDomain) -> SellerDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, id: int) -> int | None:
        raise NotImplementedError()

from abc import ABC, abstractmethod

from app.domain.models.products import ProductDomain


class IProductRepo(ABC):
    @abstractmethod
    async def get_all(self) -> list[ProductDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_id(self, id: int) -> ProductDomain:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_category(self, id: int) -> list[ProductDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def create(self, product: ProductDomain) -> ProductDomain:
        raise NotImplementedError()

    @abstractmethod
    async def update(self, id: int, product: ProductDomain) -> ProductDomain:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, id: int) -> int:
        raise NotImplementedError()

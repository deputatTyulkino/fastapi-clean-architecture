from abc import ABC, abstractmethod

from app.domain.models.categories import CategoryDomain


class ICategoryRepo(ABC):
    @abstractmethod
    async def get_all(self) -> list[CategoryDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_id(self, id: int) -> CategoryDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def exists_by_id(self, id: int) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def exists_by_name(self, name: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_name(self, name: str) -> CategoryDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def create(self, category_data: CategoryDomain) -> CategoryDomain:
        raise NotImplementedError()

    @abstractmethod
    async def update(
        self, id: int, category_data: CategoryDomain
    ) -> CategoryDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, id: int) -> int | None:
        raise NotImplementedError()

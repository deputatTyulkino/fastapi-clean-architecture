from abc import ABC, abstractmethod

from app.domain.models.orders import OrderDomain, OrderItemDomain


class IOrdersRepo(ABC):
    @abstractmethod
    async def get_all(self, user_id: int, offset: int, limit: int) -> list[OrderDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_id(self, order_id: int) -> OrderDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def create_order(self, order: OrderDomain) -> OrderDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def create_order_item(
        self, order_item: OrderItemDomain
    ) -> OrderItemDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def update_order(self, order_id: int, **kwargs) -> OrderDomain | None:
        raise NotImplementedError()

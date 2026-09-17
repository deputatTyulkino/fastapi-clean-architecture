from abc import ABC, abstractmethod
from app.domain.models.cart_items import CartItemDomain


class ICartItemsRepo(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> list[CartItemDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def create(self, cart_item_data: CartItemDomain) -> CartItemDomain:
        raise NotImplementedError()

    @abstractmethod
    async def update_quantity(self, user_id: int, product_id: int) -> CartItemDomain:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, user_id: int, product_id: int) -> int:
        raise NotImplementedError()

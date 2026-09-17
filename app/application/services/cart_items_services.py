from app.application.schemas.entities.cart_items_schemas import (
    CartItemSchema,
    CreateCartItemSchema,
)
from app.domain.interfaces.redis.i_state_client import IStateClient
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.models.cart_items import CartItemDomain


class CartItemsServices:
    def __init__(self, uow: IUnitOfWork, state_client: IStateClient):
        self.uow = uow
        self.state_client = state_client

    async def _check_user_and_product(self, user_id: int, product_id: int) -> None:
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise ValueError("Ввойдите в систему")
            product = await uow.products.get_by_id(product_id)
            if product is None:
                raise ValueError("Продукт не найден")

    async def get_all_cart_items(self, user_id: int) -> list[CartItemSchema]:
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise ValueError("Ввойдите в систему")
            cart_items = await uow.cart_items.get_by_user_id(user_id)
        return [CartItemSchema.model_validate(cart_item) for cart_item in cart_items]

    async def create_cart_item(
        self, user_id: int, cart_item_data: CreateCartItemSchema
    ) -> CartItemSchema:
        async with self.uow as uow:
            await self._check_user_and_product(user_id, cart_item_data.product_id)
            cart_item = await uow.cart_items.create(
                CartItemDomain(user_id=user_id, **cart_item_data.model_dump())
            )
        return CartItemSchema.model_validate(cart_item)

    async def update_cart_item(self, user_id: int, product_id: int) -> CartItemSchema:
        async with self.uow as uow:
            await self._check_user_and_product(user_id, product_id)
            updated_cart_item = await uow.cart_items.update_quantity(
                user_id, product_id
            )
        return CartItemSchema.model_validate(updated_cart_item)

    async def delete_cart_item(self, user_id: int, product_id: int) -> int:
        async with self.uow as uow:
            await self._check_user_and_product(user_id, product_id)
            deleted_product_id = await uow.cart_items.delete(user_id, product_id)
        return deleted_product_id

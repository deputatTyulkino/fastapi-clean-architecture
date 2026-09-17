from sqlalchemy import delete, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.repositories.i_cart_item_repo import ICartItemsRepo
from app.domain.models.cart_items import CartItemDomain
from app.infrastructure.models.cart_items import CartItemORM


class CartItemsRepo(ICartItemsRepo):
    def __init__(self, db: AsyncSession, logger: ILogger):
        self.db = db
        self.logger = logger.bind(repository="CartItemsRepo")

    def _to_domain_model(self, cart_item: CartItemORM) -> CartItemDomain:
        return CartItemDomain(
            user_id=cart_item.user_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            id=cart_item.id,
            created_at=cart_item.created_at,
            updated_at=cart_item.updated_at,
        )

    def _to_orm_model(self, cart_item: CartItemDomain) -> CartItemORM:
        return CartItemORM(
            user_id=cart_item.user_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            id=cart_item.id,
            created_at=cart_item.created_at,
            updated_at=cart_item.updated_at,
        )

    async def get_by_user_id(self, user_id: int) -> list[CartItemDomain]:
        query = select(CartItemORM).filter(CartItemORM.user_id == user_id)
        cart_items = (await self.db.scalars(query)).all()
        self.logger.debug("cart_items_fetched", user_id=user_id, count=len(cart_items))
        return [self._to_domain_model(cart_item) for cart_item in cart_items]

    async def create(self, cart_item_data: CartItemDomain) -> CartItemDomain:
        cart_item = self._to_orm_model(cart_item_data)
        self.db.add(cart_item)
        await self.db.flush()
        self.logger.info(
            "cart_item_created",
            user_id=cart_item.user_id,
            product_id=cart_item.product_id,
            cart_item_id=cart_item.id,
        )
        return self._to_domain_model(cart_item)

    async def update_quantity(self, user_id: int, product_id: int) -> CartItemDomain:
        stmt = (
            update(CartItemORM)
            .filter(
                CartItemORM.user_id == user_id, CartItemORM.product_id == product_id
            )
            .values(quantity=CartItemORM.quantity + 1)
            .returning(CartItemORM)
        )
        try:
            updated_cart_item = (await self.db.execute(stmt)).scalar_one()
        except NoResultFound:
            self.logger.warning(
                "cart_item_update_quantity_not_found",
                user_id=user_id,
                product_id=product_id,
            )
            raise
        self.logger.info(
            "cart_item_quantity_updated",
            user_id=user_id,
            product_id=product_id,
            quantity=updated_cart_item.quantity,
        )
        return self._to_domain_model(updated_cart_item)

    async def delete(self, user_id: int, product_id: int) -> int:
        stmt = (
            delete(CartItemORM)
            .filter(
                CartItemORM.user_id == user_id, CartItemORM.product_id == product_id
            )
            .returning(CartItemORM.id)
        )
        try:
            deleted_cart_items_id = (await self.db.execute(stmt)).scalar_one()
        except NoResultFound:
            self.logger.warning(
                "cart_item_delete_not_found", user_id=user_id, product_id=product_id
            )
            raise
        self.logger.info(
            "cart_item_deleted",
            user_id=user_id,
            product_id=product_id,
            cart_item_id=deleted_cart_items_id,
        )
        return deleted_cart_items_id

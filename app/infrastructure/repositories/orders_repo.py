from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.repositories.i_orders_repo import IOrdersRepo
from app.domain.models.orders import OrderDomain, OrderItemDomain
from app.infrastructure.models.orders import OrderItemORM, OrderORM


class OrdersRepo(IOrdersRepo):
    def __init__(self, db: AsyncSession, logger: ILogger):
        self.db = db
        self.logger = logger.bind(repository="OrdersRepo")

    def _to_order_item_domain_model(self, order_item: OrderItemORM) -> OrderItemDomain:
        return OrderItemDomain(
            id=order_item.id,
            product_id=order_item.product_id,
            quantity=order_item.quantity,
            unit_price=order_item.unit_price,
        )

    def _to_order_item_orm_model(self, order_item: OrderItemDomain) -> OrderItemORM:
        return OrderItemORM(
            id=order_item.id,
            product_id=order_item.product_id,
            quantity=order_item.quantity,
            unit_price=order_item.unit_price,
        )

    def _to_domain_model(self, order: OrderORM) -> OrderDomain:
        return OrderDomain(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            payment_id=order.payment_id,
            paid_at=order.paid_at,
            created_at=order.created_at,
            updated_at=order.updated_at,
            order_items=[
                self._to_order_item_domain_model(item) for item in order.items
            ],
        )

    def _to_orm_model(self, order: OrderDomain) -> OrderORM:
        return OrderORM(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            payment_id=order.payment_id,
            paid_at=order.paid_at,
            created_at=order.created_at,
            updated_at=order.updated_at,
            order_items=[
                self._to_order_item_orm_model(item) for item in order.order_items
            ],
        )

    async def get_all(self, user_id: int, offset: int, limit: int) -> list[OrderDomain]:
        query = (
            select(OrderORM)
            .filter(OrderORM.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )
        orders = (await self.db.scalars(query)).all()
        return [self._to_domain_model(order) for order in orders]

    async def get_by_id(self, order_id: int) -> OrderDomain | None:
        query = select(OrderORM).filter(OrderORM.id == order_id)
        order = (await self.db.execute(query)).scalar_one_or_none()
        if order is None:
            return None
        return self._to_domain_model(order)

    async def create_order_item(
        self, order_item: OrderItemDomain
    ) -> OrderItemDomain | None:
        created_order_item = self._to_order_item_orm_model(order_item)
        self.db.add(created_order_item)
        await self.db.flush()
        return self._to_order_item_domain_model(created_order_item)

    async def create_order(self, order: OrderDomain) -> OrderDomain | None:
        created_order = self._to_orm_model(order)
        self.db.add(created_order)
        await self.db.flush()
        return self._to_domain_model(created_order)

    async def update_order(self, order_id: int, **kwargs) -> OrderDomain | None:
        stmt = (
            update(OrderORM)
            .filter(OrderORM.id == order_id)
            .values(**kwargs)
            .returning(OrderORM)
        )
        updated_order = (await self.db.execute(stmt)).scalar_one_or_none()
        if updated_order is None:
            return None
        return self._to_domain_model(updated_order)

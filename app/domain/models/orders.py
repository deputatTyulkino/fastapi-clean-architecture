from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"


@dataclass
class OrderItemDomain:
    product_id: int
    quantity: int
    unit_price: Decimal
    order_id: int | None = None
    id: int | None = None

    @property
    def total_price(self) -> Decimal:
        return Decimal(self.quantity * self.unit_price)


@dataclass
class OrderDomain:
    user_id: int
    order_items: list[OrderItemDomain]
    status: OrderStatus = OrderStatus.pending
    id: int | None = None
    payment_id: str | None = None
    paid_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def total_amount(self) -> Decimal:
        return Decimal(sum(it.total_price for it in self.order_items))

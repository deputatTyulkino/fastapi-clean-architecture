from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.domain.models.orders import OrderStatus


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    order_id: int
    unit_price: Decimal
    quantity: int
    total_price: Decimal


class OrderSchema(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    total_amount: Decimal
    order_items: list[OrderItemResponse]


class OrderResponseSchema(OrderSchema):
    payment_id: str
    paid_at: datetime


class CheckoutOrderResponseSchema(OrderSchema):
    confirmation_url: str


class OrderStatusResponse(OrderResponseSchema):
    paid_at: datetime
    message: str

import ipaddress
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, cast

from app.application.schemas.entities.orders_schemas import (
    CheckoutOrderResponseSchema,
    OrderResponseSchema,
    OrderStatusResponse,
)
from app.application.schemas.utils.query_params_schema import OrdersParamsSchema
from app.core.config import Settings
from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.redis.i_cache_client import ICacheClient
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.interfaces.utils.exceptions import (
    AuthenticationError,
    BusinessRuleViolationError,
    EntityNotFoundError,
    InsufficientStockError,
    ProductNotFoundError,
)
from app.domain.interfaces.utils.i_payment_repo import (
    IItem,
    IPaymentRepo,
    IPaymentRequest,
    IPaymentResponse,
    IPaymentWebhookRequest,
)
from app.domain.models.orders import OrderDomain, OrderItemDomain
from app.infrastructure.redis.decorators import redis_cache


class OrdersServices:
    def __init__(
        self,
        uow: IUnitOfWork,
        cache_client: ICacheClient,
        logger: ILogger,
        payment_repo: IPaymentRepo,
        settings: Settings,
    ):
        self.uow = uow
        self.cache_client = cache_client
        self.logger = logger.bind(component="OrdersServices")
        self.payment_repo = payment_repo
        self.settings = settings
        self.ip_list: tuple[str, ...] = (
            "91.194.226.0/23",
            "91.218.132.0/24",
            "91.218.133.0/24",
            "91.218.134.0/24",
            "91.218.135.0/24",
            "212.49.24.0/24",
            "212.233.80.0/24",
            "212.233.81.0/24",
            "212.233.82.0/24",
            "212.233.83.0/24",
            "91.194.226.181",
        )

    def _is_ip_allowed(self, ip: str | None) -> bool:
        if ip is None:
            return False
        try:
            address = ipaddress.ip_address(ip)
        except ValueError:
            return False
        for mask in self.ip_list:
            if "/" in mask:
                if address in ipaddress.ip_network(mask, strict=False):
                    return True
            else:
                if address == ipaddress.ip_address(mask):
                    return True
        return False

    def _create_order_data(
        self,
        amount: int,
        order_id: str,
        customer_key: str,
        user_email: str,
        items: list[IItem],
    ) -> IPaymentRequest:
        return {
            "TerminalKey": self.settings.TERMINAL_KEY,
            "Amount": amount,
            "OrderId": order_id,
            "Token": self.settings.PAYMENT_TOKEN,
            "Description": f"Оплата заказа {order_id}",
            "CustomerKey": customer_key,
            "Recurrent": self.settings.RECURRENT,
            "NotificationURL": self.settings.NOTIFICATION_URL,
            "Receipt": {
                "Items": [
                    {
                        "Name": item["Name"],
                        "Price": item["Price"],
                        "Quantity": item["Quantity"],
                        "Amount": item["Amount"],
                        "Tax": self.settings.TAX,
                    }
                    for item in items
                ],
                "Email": user_email,
                "Taxation": self.settings.TAXATION,
            },
        }

    def _convert_price(self, price: Decimal) -> int:
        return int(price * 100)

    @redis_cache(
        lambda user_id: f"users:{user_id}:orders", 1000, list[OrderResponseSchema]
    )
    async def get_all_orders(
        self, user_id: int, query_params: OrdersParamsSchema
    ) -> list[OrderResponseSchema]:
        self.logger.debug(
            "get_all_orders_started",
            user_id=user_id,
            offset=query_params.offset,
            limit=query_params.limit,
        )
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                self.logger.warning("get_all_orders_user_not_found", user_id=user_id)
                raise AuthenticationError("Ввойдите в систему")
            orders = await uow.orders.get_all(
                user_id, query_params.offset, query_params.limit
            )
        self.logger.info("get_all_orders_success", user_id=user_id, count=len(orders))
        return [OrderResponseSchema.model_validate(order) for order in orders]

    @redis_cache(
        lambda order_id, user_id: f"users:{user_id}:orders:{order_id}",
        1000,
        OrderResponseSchema,
    )
    async def get_order(self, order_id: int, user_id: int) -> OrderResponseSchema:
        self.logger.debug("get_order_started", order_id=order_id, user_id=user_id)
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                self.logger.warning("get_order_user_not_found", user_id=user_id)
                raise AuthenticationError("Ввойдите в систему")
            order = await uow.orders.get_by_id(order_id)
            if order is None:
                self.logger.warning(
                    "get_order_not_found", order_id=order_id, user_id=user_id
                )
                raise EntityNotFoundError(f"Заказа с ID {order_id} не существует")
        self.logger.debug("get_order_success", order_id=order_id, user_id=user_id)
        return OrderResponseSchema.model_validate(order)

    async def create_order(self, user_id: int) -> CheckoutOrderResponseSchema:
        self.logger.info("create_order_started", user_id=user_id)
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                self.logger.warning("create_order_user_not_found", user_id=user_id)
                raise AuthenticationError("Ввойдите в систему")
            cart_items = await uow.cart_items.get_by_user_id(user_id)
            if len(cart_items) == 0:
                self.logger.warning("create_order_empty_cart", user_id=user_id)
                raise EntityNotFoundError("Корзина пуста")
            order = await uow.orders.create_order(OrderDomain(user_id))
            if order is None:
                self.logger.error("create_order_db_failed", user_id=user_id)
                raise BusinessRuleViolationError("Ошибка сервера")
            order_items_data: list[IItem] = []
            for cart_item in cart_items:
                product = await uow.products.get_by_id(cart_item.product_id)
                if product is None or not product.is_active:
                    self.logger.warning(
                        "create_order_product_unavailable",
                        user_id=user_id,
                        order_id=order.id,
                        product_id=cart_item.product_id,
                        exists=product is not None,
                    )
                    raise ProductNotFoundError("Продукт не активен")
                if product.stock < cart_item.quantity:
                    self.logger.warning(
                        "create_order_insufficient_stock",
                        user_id=user_id,
                        order_id=order.id,
                        product_id=product.id,
                        requested=cart_item.quantity,
                        available=product.stock,
                    )
                    raise InsufficientStockError(
                        f"Недостаточно {product.name} на складе"
                    )
                order_item = await uow.orders.create_order_item(
                    OrderItemDomain(
                        product_id=cart_item.product_id,
                        quantity=cart_item.quantity,
                        unit_price=product.price,
                    )
                )
                if order_item is None:
                    self.logger.error(
                        "create_order_item_db_failed",
                        user_id=user_id,
                        order_id=order.id,
                        product_id=cart_item.product_id,
                    )
                    raise BusinessRuleViolationError("Ошибка сервера")
                order.order_items.append(order_item)
                product.stock -= cart_item.quantity
                order_items_data.append(
                    {
                        "Name": product.name,
                        "Price": self._convert_price(order_item.unit_price),
                        "Quantity": order_item.quantity,
                        "Amount": self._convert_price(order_item.total_price),
                        "Tax": self.settings.TAX,
                    }
                )
            order = await uow.orders.update_order(
                cast(int, order.id),
                order_items=order.order_items,
            )
            if order is None:
                self.logger.error("create_order_update_failed", user_id=user_id)
                raise BusinessRuleViolationError("Ошибка сервера")
            self.logger.info(
                "create_order_items_reserved",
                user_id=user_id,
                order_id=order.id,
                items_count=len(order_items_data),
            )
            payment_data: (
                IPaymentResponse | None
            ) = await self.payment_repo.create_payment(
                self._create_order_data(
                    self._convert_price(order.total_amount),
                    str(cast(int, order.id)),
                    str(user_id),
                    user.email,
                    order_items_data,
                )
            )
            if payment_data is None:
                self.logger.error(
                    "create_order_payment_no_response",
                    user_id=user_id,
                    order_id=order.id,
                )
                raise BusinessRuleViolationError("Возникла ошибка при оплате")
            if not payment_data["Success"]:
                self.logger.error(
                    "create_order_payment_rejected",
                    user_id=user_id,
                    order_id=order.id,
                )
                raise BusinessRuleViolationError("Возникла ошибка при оплате")
            self.logger.info(
                "create_order_payment_created", user_id=user_id, order_id=order.id
            )
            async with self.uow as uow:
                deleted_cart_items_ids = await uow.cart_items.delete_all(user_id)
                if deleted_cart_items_ids is None:
                    self.logger.error(
                        "create_order_cart_clear_failed",
                        user_id=user_id,
                        order_id=order.id,
                    )
                    raise BusinessRuleViolationError("Ошибка сервера")
                updated_order = await uow.orders.update_order(
                    cast(int, order.id), payment_id=payment_data["PaymentURL"]
                )
                if updated_order is None:
                    self.logger.error(
                        "create_order_payment_id_update_failed",
                        user_id=user_id,
                        order_id=order.id,
                    )
                    raise BusinessRuleViolationError("Ошибка сервера")
                await uow.commit()
            await self.cache_client.delete(f"users:{user_id}:orders")
            await self.cache_client.delete(f"users:{user_id}:orders:{order.id}")
            self.logger.info(
                "create_order_success", user_id=user_id, order_id=updated_order.id
            )
            return CheckoutOrderResponseSchema(
                **updated_order.as_dict(), confirmation_url=payment_data["PaymentURL"]
            )

    @redis_cache(
        lambda order_id, user_id: f"users:{user_id}:orders:{order_id}:status",
        1000,
        OrderStatusResponse,
    )
    async def get_order_status(
        self, order_id: int, user_id: int
    ) -> OrderStatusResponse:
        self.logger.debug(
            "get_order_status_started", order_id=order_id, user_id=user_id
        )
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                self.logger.warning("get_order_status_user_not_found", user_id=user_id)
                raise AuthenticationError("Ввойдите в систему")
            order = await uow.orders.get_by_id(order_id)
            if order is None:
                self.logger.warning(
                    "get_order_status_not_found", order_id=order_id, user_id=user_id
                )
                raise EntityNotFoundError(f"Заказ с ID {order_id} не найден")
            message = ""
            if order.status == "paid":
                message = f"Спасибо! Заказ #{order_id} оплачен. Ожидайте доставку."
            elif order.status in ["canceled", "failed"]:
                message = "Оплата не прошла. Попробуйте ещё раз."
            else:
                message = "Оплата в процессе..."
        self.logger.debug(
            "get_order_status_success",
            order_id=order_id,
            user_id=user_id,
            status=order.status,
        )
        return OrderStatusResponse(**order.as_dict(), message=message)

    async def res_accept_payment(
        self, client_ip: str | None, payment_data: IPaymentWebhookRequest
    ):
        if not self._is_ip_allowed(client_ip):
            self.logger.warning("payment_webhook_ip_forbidden", client_ip=client_ip)
            raise AuthenticationError("Недоступный IP")
        order_id = int(payment_data["OrderId"])
        bank_status = payment_data["Status"]
        self.logger.info(
            "payment_webhook_received",
            order_id=order_id,
            bank_status=bank_status,
            payment_id=payment_data.get("PaymentId"),
            client_ip=client_ip,
        )
        async with self.uow as uow:
            order = await uow.orders.get_by_id(order_id)
            if order is None:
                self.logger.warning(
                    "payment_webhook_order_not_found", order_id=order_id
                )
                return {"status": "ignored"}
            data_for_update_order: dict[str, Any] = {"status": "paid"}
            if bank_status == "CANCELED":
                data_for_update_order["status"] = "canceled"
            elif bank_status == "REJECTED":
                data_for_update_order["status"] = "failed"
            elif bank_status == "CONFIRMED":
                data_for_update_order["paid_at"] = datetime.now(timezone.utc)
                data_for_update_order["payment_id"] = payment_data["PaymentId"]
            updated_order = await uow.orders.update_order(
                cast(int, order.id), **data_for_update_order
            )
            if updated_order is None:
                self.logger.error("payment_webhook_update_failed", order_id=order_id)
                return {"status": "ignored"}
            await uow.commit()
        self.logger.info(
            "payment_webhook_processed",
            order_id=order_id,
            bank_status=bank_status,
            old_status=order.status,
            new_status=data_for_update_order["status"],
        )
        return {"status": "ok"}

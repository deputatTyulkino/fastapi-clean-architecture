from typing import Annotated

from fastapi import Depends

from app.application.services.orders_services import OrdersServices
from app.infrastructure.depends.entities.orders_services import get_orders_services_infr


def get_orders_services(
    services: Annotated[OrdersServices, Depends(get_orders_services_infr)],
) -> OrdersServices:
    return services

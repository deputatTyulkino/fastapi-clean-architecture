from typing import Annotated

from fastapi import Depends

from app.application.services.cart_items_services import CartItemsServices
from app.infrastructure.depends.entities.cart_item_services import (
    get_cart_items_services_infr,
)


def get_cart_items_services(
    services: Annotated[CartItemsServices, Depends(get_cart_items_services_infr)],
) -> CartItemsServices:
    return services

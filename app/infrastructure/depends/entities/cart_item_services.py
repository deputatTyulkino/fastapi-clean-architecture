from typing import Annotated

from fastapi import Depends

from app.application.services.cart_items_services import CartItemsServices
from app.domain.interfaces.redis.i_state_client import IStateClient
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.infrastructure.depends.utils.redis_depends import get_state_client
from app.infrastructure.uow.depends import get_uow_infr


def get_cart_items_services_infr(
    uow: Annotated[IUnitOfWork, Depends(get_uow_infr)],
    state_client: Annotated[IStateClient, Depends(get_state_client)],
) -> CartItemsServices:
    return CartItemsServices(uow, state_client)

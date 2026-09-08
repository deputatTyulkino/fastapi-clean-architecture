from typing import Annotated

from fastapi import Depends

from app.application.services.reviews_services import ReviewServices
from app.domain.interfaces.redis.i_cache_client import ICacheClient
from app.domain.interfaces.redis.i_state_client import IStateClient
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.infrastructure.depends.utils.redis_depends import (
    get_cache_client,
    get_state_client,
)
from app.infrastructure.uow.depends import get_uow_infr


def get_reviews_services(
    uow: Annotated[IUnitOfWork, Depends(get_uow_infr)],
    cache_client: Annotated[ICacheClient, Depends(get_cache_client)],
    state_client: Annotated[IStateClient, Depends(get_state_client)],
) -> ReviewServices:
    return ReviewServices(uow, cache_client, state_client)

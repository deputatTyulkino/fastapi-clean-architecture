from typing import Annotated

from fastapi import Depends

from app.application.services.categories_services import CategoryServices
from app.domain.interfaces.redis.i_cache_client import ICacheClient
from app.infrastructure.depends.utils.redis_depends import get_cache_client
from app.infrastructure.uow.depends import get_uow_infr
from app.infrastructure.uow.uow import UnitOfWork


def get_categories_services_infr(
    uow: Annotated[UnitOfWork, Depends(get_uow_infr)],
    cache_client: Annotated[ICacheClient, Depends(get_cache_client)],
) -> CategoryServices:
    return CategoryServices(uow, cache_client)

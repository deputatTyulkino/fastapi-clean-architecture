from typing import Annotated

from fastapi import Depends

from app.application.services.sellers_services import SellerServices
from app.domain.interfaces.redis.i_cache_client import ICacheClient
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.interfaces.utils.i_image_storage import IImageServices
from app.infrastructure.depends.utils.image_storage import get_image_services
from app.infrastructure.depends.utils.redis_depends import get_cache_client
from app.infrastructure.uow.depends import get_uow_infr


def get_sellers_services_infr(
    uow: Annotated[IUnitOfWork, Depends(get_uow_infr)],
    image_services: Annotated[IImageServices, Depends(get_image_services)],
    cache_client: Annotated[ICacheClient, Depends(get_cache_client)],
) -> SellerServices:
    return SellerServices(uow, image_services, cache_client)

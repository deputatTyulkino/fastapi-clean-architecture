from typing import Annotated

from fastapi import Depends

from app.application.services.sellers_services import SellerServices
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.infrastructure.uow.depends import get_uow_infr
from app.infrastructure.utils.image_storage import ImageStorage


def get_sellers_services_infr(
    uow: Annotated[IUnitOfWork, Depends(get_uow_infr)],
) -> SellerServices:
    image_storage = ImageStorage()
    return SellerServices(uow, image_storage)

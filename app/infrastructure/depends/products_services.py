from typing import Annotated

from fastapi import Depends

from app.application.services.products_services import ProductServices
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.infrastructure.uow.depends import get_uow_infr
from app.infrastructure.utils.image_storage import ImageStorage


def get_products_services_infr(
    uow: Annotated[IUnitOfWork, Depends(get_uow_infr)],
) -> ProductServices:
    image_storage = ImageStorage()
    return ProductServices(uow, image_storage)

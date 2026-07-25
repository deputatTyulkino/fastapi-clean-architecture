from typing import Annotated

from fastapi import Depends

from app.application.services.categories_services import CategoryServices
from app.infrastructure.uow.depends import get_uow_infr
from app.infrastructure.uow.uow import UnitOfWork


def get_categories_services_infr(
    uow: Annotated[UnitOfWork, Depends(get_uow_infr)],
) -> CategoryServices:
    return CategoryServices(uow)

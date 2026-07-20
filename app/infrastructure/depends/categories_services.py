from fastapi import Depends

from app.application.services.categories_services import CategoryServices
from app.infrastructure.uow.depends import get_uow
from app.infrastructure.uow.uow import UnitOfWork


def get_categories_services_infr(
    uow: UnitOfWork = Depends(get_uow),
) -> CategoryServices:
    return CategoryServices(uow)

from typing import Annotated

from fastapi import Depends

from app.application.services.reviews_services import ReviewServices
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.infrastructure.uow.depends import get_uow_infr


def get_reviews_services(
    uow: Annotated[IUnitOfWork, Depends(get_uow_infr)],
) -> ReviewServices:
    return ReviewServices(uow)

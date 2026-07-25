from typing import Annotated

from fastapi import Depends

from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.infrastructure.uow.depends import get_uow_infr


def get_uow(uow: Annotated[IUnitOfWork, Depends(get_uow_infr)]) -> IUnitOfWork:
    return uow

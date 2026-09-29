from typing import Annotated

from fastapi import Request

from app.domain.interfaces.logging.i_logger import ILogger
from app.infrastructure.logging.logger import get_logger
from app.infrastructure.uow.uow import UnitOfWork


def get_uow_infr(request: Request, logger: Annotated[ILogger, get_logger]):
    return UnitOfWork(request.app.state.session_factory, logger)

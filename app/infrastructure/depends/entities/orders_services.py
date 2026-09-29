from typing import Annotated

from fastapi import Depends

from app.application.services.orders_services import OrdersServices
from app.core.config import Settings, get_settings
from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.redis.i_cache_client import ICacheClient
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.interfaces.utils.i_payment_repo import IPaymentRepo
from app.infrastructure.depends.utils.payment_repo import get_payment_repo_infr
from app.infrastructure.depends.utils.redis_depends import get_cache_client
from app.infrastructure.logging.logger import get_logger
from app.infrastructure.uow.depends import get_uow_infr


def get_orders_services_infr(
    uow: Annotated[IUnitOfWork, Depends(get_uow_infr)],
    cache_client: Annotated[ICacheClient, Depends(get_cache_client)],
    logger: Annotated[ILogger, Depends(get_logger)],
    payment_repo: Annotated[IPaymentRepo, Depends(get_payment_repo_infr)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> OrdersServices:
    return OrdersServices(uow, cache_client, logger, payment_repo, settings)

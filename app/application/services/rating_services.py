from typing import cast

from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.infrastructure.depends.utils.redis_depends import (
    get_redis_manager_infr,
    get_state_client,
)
from app.infrastructure.logging.logger import get_logger

_logger: ILogger = get_logger(component="recalculate_products_rating")


async def recalculate_products_rating(uow: IUnitOfWork):
    redis_manager = get_redis_manager_infr()
    state_client = get_state_client()
    token = await redis_manager.acquire_lock("acquire:token:lock", 150)
    if token is None:
        _logger.info("products_rating_recalc_skipped", reason="lock_not_acquired")
        return
    set_products_ids = cast(set[str], await state_client.smembers("dirty_products_ids"))
    products_ids = [int(el.split(":")[1]) for el in set_products_ids]
    async with uow:
        await uow.products.update_reviews_statistics(products_ids)
        await uow.commit()
    await redis_manager.release_lock("acquire:token:lock", token)
    _logger.info("products_rating_recalculated", count=len(products_ids))

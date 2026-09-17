from typing import cast

from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.infrastructure.depends.utils.redis_depends import (
    get_redis_manager_infr,
    get_state_client,
)


async def recalculate_products_rating(uow: IUnitOfWork):
    redis_manager = get_redis_manager_infr()
    state_client = get_state_client()
    token = await redis_manager.acquire_lock("acquire:token:lock", 150)
    if token is None:
        return
    set_products_ids = cast(set[str], await state_client.smembers("dirty_products_ids"))
    products_ids = [int(el.split(":")[1]) for el in set_products_ids]
    async with uow:
        await uow.products.update_reviews_statistics(products_ids)
        await uow.commit()
    await redis_manager.release_lock("acquire:token:lock", token)

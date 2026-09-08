from typing import cast

from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.infrastructure.depends.utils.redis_depends import get_state_client


async def recalculate_products_rating(uow: IUnitOfWork):
    state_client = get_state_client()
    set_products_ids = cast(set[str], await state_client.smembers("dirty_products_ids"))
    products_ids = [int(el.split(":")[1]) for el in set_products_ids]
    async with uow:
        await uow.products.update_reviews_statistics(products_ids)
        await uow.commit()

from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork


async def recalculate_products_rating(uow: IUnitOfWork, product_ids: list[int]):
    async with uow:
        await uow.products.update_reviews_statistics(product_ids)
        await uow.commit()

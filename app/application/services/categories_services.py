from app.application.schemas.entities.categories_schemas import (
    CategorySchema,
    CreateCategorySchema,
    UpdateCategorySchema,
)
from app.application.schemas.utils.success_delete_schema import SuccessDeleteSchema
from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.redis.i_cache_client import ICacheClient
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.interfaces.utils.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    ProductNotFoundError,
)
from app.domain.models.categories import CategoryDomain
from app.infrastructure.redis.decorators import redis_cache


class CategoryServices:
    def __init__(self, uow: IUnitOfWork, cache_client: ICacheClient, logger: ILogger):
        self.uow = uow
        self.cache_client = cache_client
        self.logger = logger.bind(component="CategoryServices")

    @redis_cache(lambda _: "all_categories", 10000, list[CategorySchema])
    async def get_all_categories(self) -> list[CategorySchema]:
        async with self.uow as uow:
            categories = await uow.categories.get_all()
        return [CategorySchema.model_validate(category) for category in categories]

    @redis_cache(lambda id: f"categories:{id}", 10000, CategorySchema)
    async def get_category_by_id(self, id: int) -> CategorySchema:
        async with self.uow as uow:
            category = await uow.categories.get_by_id(id)
        if category is None:
            self.logger.warning(
                "category_lookup_failed", category_id=id, reason="not_found"
            )
            raise CategoryNotFoundError(f"Категории с ID {id} не существует")
        return CategorySchema.model_validate(category)

    @redis_cache(
        lambda product_id: f"categories:products:{product_id}", 1000, CategorySchema
    )
    async def get_category_by_product(self, product_id: int) -> CategorySchema:
        async with self.uow as uow:
            exists_product = await uow.products.exists_by_id(product_id)
            if not exists_product:
                self.logger.warning(
                    "category_lookup_by_product_failed",
                    product_id=product_id,
                    reason="product_not_found",
                )
                raise ProductNotFoundError(f"Продукта с ID {product_id} не существует")
            category = await uow.categories.get_by_product_id(product_id)
            if category is None:
                self.logger.warning(
                    "category_lookup_by_product_failed",
                    product_id=product_id,
                    reason="category_not_found",
                )
                raise CategoryNotFoundError("Категория не найдена")
        return CategorySchema.model_validate(category)

    async def create_category(
        self, category_data: CreateCategorySchema
    ) -> CategorySchema:
        async with self.uow as uow:
            exists_category = await uow.categories.exists_by_name(category_data.name)
            if exists_category:
                self.logger.warning(
                    "category_creation_rejected",
                    name=category_data.name,
                    reason="name_taken",
                )
                raise CategoryAlreadyExistsError(
                    f"Категория с именем {category_data.name} уже существует"
                )
            new_category = await uow.categories.create(
                CategoryDomain(**category_data.model_dump())
            )
            await uow.commit()
        await self.cache_client.delete("all_categories")
        return CategorySchema.model_validate(new_category)

    async def update_category(
        self, id: int, category_data: UpdateCategorySchema
    ) -> CategorySchema:
        async with self.uow as uow:
            exists_category = await uow.categories.exists_by_id(id)
            if not exists_category:
                self.logger.warning(
                    "category_update_rejected", category_id=id, reason="not_found"
                )
                raise CategoryNotFoundError(f"Категории с ID {id} не существует")
            updated_category = await uow.categories.update(
                id, CategoryDomain(**category_data.model_dump())
            )
            await uow.commit()
        await self.cache_client.delete("all_categories", f"categories:{id}")
        return CategorySchema.model_validate(updated_category)

    async def delete_category(self, id: int) -> SuccessDeleteSchema:
        async with self.uow as uow:
            category = await uow.categories.get_by_id(id)
            if category is None:
                self.logger.warning(
                    "category_delete_rejected", category_id=id, reason="not_found"
                )
                raise CategoryNotFoundError(f"Категории с id {id} не существует")
            cat_id = await uow.categories.delete(id)
            await uow.commit()
        await self.cache_client.delete("all_categories", f"categories:{id}")
        return SuccessDeleteSchema(detail=f"Категория с ID {cat_id} успешно удалена")

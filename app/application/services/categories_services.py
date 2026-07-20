from app.application.schemas.categories_schemas import (
    CategorySchema,
    CreateCategorySchema,
    SuccessDelereCategorySchema,
    UpdateCategorySchema,
)
from app.domain.interfaces_uow.i_unit_of_work import IUnitOfWork
from app.domain.models.categories import CategoryDomain


class CategoryServices:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_all_categories(self) -> list[CategorySchema]:
        async with self.uow as uow:
            categories = await uow.categories.get_all()
        return (
            [CategorySchema.model_validate(category) for category in categories]
            if categories
            else []
        )

    async def get_category_by_id(self, id: int) -> CategorySchema:
        async with self.uow as uow:
            category = await uow.categories.get_by_id(id)
        if category is None:
            raise ValueError(f"Категории с ID {id} не существует")
        return CategorySchema.model_validate(category)

    async def create_category(
        self, category_data: CreateCategorySchema
    ) -> CategorySchema:
        async with self.uow as uow:
            category = await uow.categories.get_by_name(category_data.name)
            if category is not None:
                raise ValueError(f"Категория с именем {category.name} уже существует")
            new_category = await uow.categories.create(
                CategoryDomain(name=category_data.name)
            )
            await uow.commit()
        return CategorySchema.model_validate(new_category)

    async def update_category(
        self, id: int, category_data: UpdateCategorySchema
    ) -> CategorySchema:
        async with self.uow as uow:
            category = await uow.categories.get_by_id(id)
            if category is None:
                raise ValueError(f"Категории с ID {id} не существует")
            updated_category = await uow.categories.update(
                id, CategoryDomain(name=category_data.name)
            )
            await uow.commit()
        return CategorySchema.model_validate(updated_category)

    async def delete_category(self, id: int) -> SuccessDelereCategorySchema:
        async with self.uow as uow:
            category = await uow.categories.get_by_id(id)
            if category is None:
                raise ValueError(f"Категории с id {id} не существует")
            cat_id = await uow.categories.delete(id)
        return SuccessDelereCategorySchema.model_validate(
            f"Категория с ID {cat_id} успешно удалена"
        )

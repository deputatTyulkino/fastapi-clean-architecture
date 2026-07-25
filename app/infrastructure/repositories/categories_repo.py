from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.repositories.i_category_repo import ICategoryRepo
from app.domain.models.categories import CategoryDomain
from app.infrastructure.models.categories import CategoryORM


class CategoryRepo(ICategoryRepo):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_orm_model(self, category: CategoryDomain) -> CategoryORM:
        return CategoryORM(
            id=category.id, name=category.name, is_active=category.is_active
        )

    def _to_domain_model(self, category: CategoryORM) -> CategoryDomain:
        return CategoryDomain(
            id=category.id, name=category.name, is_active=category.is_active
        )

    async def get_all(self) -> list[CategoryDomain]:
        query = select(CategoryORM).filter(CategoryORM.is_active)
        data = (await self.db.scalars(query)).all()
        return [self._to_domain_model(category) for category in data]

    async def get_by_id(self, id: int) -> CategoryDomain | None:
        query = select(CategoryORM).filter(CategoryORM.id == id, CategoryORM.is_active)
        data = (await self.db.execute(query)).scalar_one_or_none()
        if data is None:
            return None
        return self._to_domain_model(data)

    async def get_by_name(self, name: str) -> CategoryDomain | None:
        query = select(CategoryORM).filter(
            CategoryORM.name == name, CategoryORM.is_active
        )
        data = (await self.db.execute(query)).scalar_one_or_none()
        if data is None:
            return None
        return self._to_domain_model(data)

    async def exists_by_id(self, id: int) -> bool:
        stmt = select(exists().where(CategoryORM.id == id, CategoryORM.is_active))
        return bool(await self.db.scalar(stmt))

    async def exists_by_name(self, name: str) -> bool:
        stmt = select(exists().where(CategoryORM.name == name, CategoryORM.is_active))
        return bool(await self.db.scalar(stmt))

    async def create(self, category_data: CategoryDomain) -> CategoryDomain:
        category = self._to_orm_model(category_data)
        self.db.add(category)
        await self.db.flush()
        return self._to_domain_model(category)

    async def update(
        self, id: int, category_data: CategoryDomain
    ) -> CategoryDomain | None:
        stmt = (
            update(CategoryORM)
            .filter(CategoryORM.id == id)
            .values(category_data.filtered_none_fields())
            .returning(CategoryORM)
        )
        category = (await self.db.execute(stmt)).scalar_one_or_none()
        if category is None:
            return None
        return self._to_domain_model(category)

    async def delete(self, id: int) -> int | None:
        stmt = (
            update(CategoryORM)
            .filter(CategoryORM.id == id)
            .values(is_active=False)
            .returning(CategoryORM.id)
        )
        cat_id = (await self.db.execute(stmt)).scalar_one_or_none()
        return cat_id

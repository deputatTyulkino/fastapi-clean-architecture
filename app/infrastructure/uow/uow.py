from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.interfaces.repositories.i_category_repo import ICategoryRepo
from app.domain.interfaces.repositories.i_product_repo import IProductRepo
from app.domain.interfaces.repositories.i_user_repo import IUserRepo
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.infrastructure.repositories.categories_repo import CategoryRepo
from app.infrastructure.repositories.products_repo import ProductRepo
from app.infrastructure.repositories.users_repo import UserRepo


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory: async_sessionmaker[AsyncSession] = session_factory
        self.session: AsyncSession | None = None
        self._users: IUserRepo | None = None
        self._categories: ICategoryRepo | None = None
        self._products: IProductRepo | None = None

    @property
    def users(self) -> IUserRepo:
        if self._users is None:
            raise RuntimeError(
                "UnitOfWork не инициализирован. Используйте блок 'async with'"
            )
        return self._users

    @property
    def categories(self) -> ICategoryRepo:
        if self._categories is None:
            raise RuntimeError(
                "UnitOfWork не инициализирован. Используйте блок 'async with'"
            )
        return self._categories

    @property
    def products(self) -> IProductRepo:
        if self._products is None:
            raise RuntimeError(
                "UnitOfWork не инициализирован. Используйте блок 'async with'"
            )
        return self._products

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        self._users = UserRepo(self.session)
        self._categories = CategoryRepo(self.session)
        self._products = ProductRepo(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if self.session:
                await self.session.close()
            self.session = None
            self._users = None

    async def commit(self) -> None:
        if self.session:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session:
            await self.session.rollback()

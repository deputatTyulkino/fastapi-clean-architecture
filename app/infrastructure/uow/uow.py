from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.interfaces_repo.i_user_repo import IUserRepo
from app.domain.interfaces_uow.i_unit_of_work import IUnitOfWork
from app.infrastructure.repositories.users_repo import UserRepo


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory: async_sessionmaker[AsyncSession] = session_factory
        self.session: AsyncSession | None = None
        self._users: IUserRepo | None = None

    @property
    def users(self) -> IUserRepo:
        if self._users is None:
            raise RuntimeError(
                "UnitOfWork не инициализирован. Используйте блок 'async with'"
            )
        return self._users

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        self._users = UserRepo(self.session)
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

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.repositories.i_user_repo import IUserRepo
from app.domain.models.users import UserDomain
from app.infrastructure.models.users import UserORM


class UserRepo(IUserRepo):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_orm_model(self, user: UserDomain) -> UserORM:
        return UserORM(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            role=user.role,
        )

    def _to_domain_model(self, user: UserORM) -> UserDomain:
        return UserDomain(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            role=user.role,
        )

    async def get_by_email(self, email: str) -> UserDomain | None:
        query = select(UserORM).filter_by(email=email)
        user = (await self.db.execute(query)).scalar_one_or_none()
        if user is None:
            return None
        return self._to_domain_model(user)

    async def create(self, user: UserDomain) -> UserDomain:
        new_user = self._to_orm_model(user)
        self.db.add(new_user)
        await self.db.flush()
        return self._to_domain_model(new_user)

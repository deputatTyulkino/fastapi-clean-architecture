from abc import ABC, abstractmethod

from app.domain.models.users import UserDomain


class IUserRepo(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> UserDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def create(self, user: UserDomain) -> UserDomain:
        raise NotImplementedError()

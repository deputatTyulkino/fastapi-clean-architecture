from abc import ABC, abstractmethod
from typing import Self

from app.domain.interfaces_repo.i_user_repo import IUserRepo



class IUnitOfWork(ABC):
    users: IUserRepo
    async def __aenter__(self) -> Self:
        raise NotImplementedError()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError()

from abc import ABC, abstractmethod


class IRefreshTokenRepo(ABC):
    @abstractmethod
    async def create(self, token_hash: str, user_id: int, family_id: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def get(self, token_hash: str) -> dict | None:
        raise NotImplementedError()

    @abstractmethod
    async def rotate(
        self, old_token_hash: str, new_token_hash: str, user_id: int, family_id: str
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def revoke_family(self, family_id: str) -> None:
        raise NotImplementedError()

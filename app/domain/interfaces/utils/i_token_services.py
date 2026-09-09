from abc import ABC, abstractmethod


class ITokenServices(ABC):
    @abstractmethod
    def decode_token(self, token: str) -> dict | None:
        raise NotImplementedError()

    @abstractmethod
    def hash_password(self, password: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def create_access_token(self, data: dict) -> str:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def create_refresh_token() -> str:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def hash_refresh_token(token_raw: str) -> str:
        raise NotImplementedError()

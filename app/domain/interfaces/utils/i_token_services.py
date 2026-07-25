from abc import ABC, abstractmethod
from typing import Literal


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
    def create_token(self, data: dict, token_type: Literal["access", "refresh"]) -> str:
        raise NotImplementedError()

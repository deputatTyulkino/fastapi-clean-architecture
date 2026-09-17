from abc import ABC, abstractmethod


class IMailManager(ABC):
    @abstractmethod
    async def send_mail_for_verify(self, email: str, code: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def generate_verification_code(self) -> str:
        raise NotImplementedError()

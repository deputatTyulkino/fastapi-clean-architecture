from abc import ABC, abstractmethod

from app.domain.models.files import FileDomain


class IImageServices(ABC):
    @abstractmethod
    async def save_image(self, file: FileDomain, file_slug: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def remove_image(self, image_url: str) -> None:
        raise NotImplementedError()

import uuid
from pathlib import Path
from typing import cast

import aiofiles
from PIL import Image, UnidentifiedImageError

from app.domain.interfaces.utils.i_image_storage import IImageStorage
from app.domain.models.files import FileDomain


class ImageStorage(IImageStorage):
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.MEDIA_ROOT = self.BASE_DIR / "media"
        self.ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
        self.MIME_TO_EXTENSION = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }
        self.CHUNK_SIZE = 1024 * 1024
        self.MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024

    async def save_image(self, file: FileDomain, file_slug: str) -> str:
        """
        Сохраняет изображение товара и возвращает относительный URL.
        """
        media_dir = self.MEDIA_ROOT / file_slug
        media_dir.mkdir(parents=True, exist_ok=True)
        extension = self.MIME_TO_EXTENSION[cast(str, file.content_type)]
        file_name = f"{uuid.uuid4()}{extension}"
        file_path = media_dir / file_name
        total_size = 0
        try:
            async with aiofiles.open(file_path, "wb") as buffer:
                while chunk := await file.file_object.read(self.CHUNK_SIZE):
                    total_size += len(chunk)
                    if total_size >= self.MAX_FILE_SIZE_BYTES:
                        raise ValueError("Файл превышает допустимый размер")
                    await buffer.write(chunk)
            try:
                with Image.open(file_path) as img:
                    img.verify()
            except UnidentifiedImageError:
                file_path.unlink(missing_ok=True)
                raise ValueError("Некорректный или поврежденный файл изображения")
            return f"/media/{file_slug}/{file_name}"
        finally:
            await file.file_object.close()

    async def remove_image(self, image_url: str) -> None:
        """
        Удаляет файл изображения, если он существует.
        """
        if not image_url:
            return
        file_path = (self.BASE_DIR / image_url.lstrip("/")).resolve()
        if not file_path.is_relative_to(self.MEDIA_ROOT.resolve()):
            return
        file_path.unlink(missing_ok=True)

from fastapi import HTTPException, UploadFile, status

ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def check_file_extension(file: UploadFile) -> UploadFile:
    if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Неподдерживаемый формат файла",
        )
    return file


def check_file_extension_for_update(file: UploadFile | None) -> UploadFile | None:
    if file and file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Неподдерживаемый формат файла",
        )
    return file

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.entities.categories_schemas import (
    CategorySchema,
    CreateCategorySchema,
    UpdateCategorySchema,
)
from app.application.schemas.utils.success_delete_schema import SuccessDeleteSchema
from app.application.schemas.utils.success_response_schema import SuccessResponseSchema
from app.application.services.categories_services import CategoryServices
from app.presentation.depends.entities.categories_services import (
    get_categories_services,
)
from app.presentation.depends.utils.check_user import get_current_admin

router = APIRouter(prefix="/categories")


@router.get(
    "/",
    tags=["categories"],
    response_model=SuccessResponseSchema[list[CategorySchema]],
    status_code=status.HTTP_200_OK,
    summary="Получить все категории",
)
async def get_all_categories(
    services: Annotated[CategoryServices, Depends(get_categories_services)],
):
    """
    Получить список всех категорий.

    **Возвращает**:
    - `data`: массив объектов `CategorySchema` с информацией о каждой категории.

    **Ошибки**: не предусмотрены (всегда возвращает 200 OK, даже если список пуст).
    """
    data = await services.get_all_categories()
    return SuccessResponseSchema(data=data)


@router.get(
    "/{id}",
    tags=["categories"],
    response_model=SuccessResponseSchema[CategorySchema],
    status_code=status.HTTP_200_OK,
    summary="Получить категорию по ID",
)
async def get_category_by_id(
    id: int,
    services: Annotated[CategoryServices, Depends(get_categories_services)],
):
    """
    Получить категорию по её идентификатору.

    - **id** (path): числовой идентификатор категории.

    **Возвращает**:
    - `data`: объект `CategorySchema` с данными запрошенной категории.

    **Возможные ошибки**:
    - `404 Not Found`: категория с указанным `id` не найдена.
    """
    try:
        data = await services.get_category_by_id(id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/",
    tags=["categories"],
    response_model=SuccessResponseSchema[CategorySchema],
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую категорию",
    dependencies=[Depends(get_current_admin)],
)
async def create_category(
    category_data: Annotated[
        CreateCategorySchema, Depends(CreateCategorySchema.as_form)
    ],
    services: Annotated[CategoryServices, Depends(get_categories_services)],
):
    """
    Создать новую категорию.

    **Тело запроса** (JSON):
    - Поля, соответствующие схеме `CreateCategorySchema`.

    **Возвращает**:
    - `data`: созданный объект `CategorySchema` (с присвоенным `id`).

    **Возможные ошибки**:
    - `409 Conflict`: категория с таким именем уже существует.
    """
    try:
        data = await services.create_category(category_data)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch(
    "/{id}",
    tags=["categories"],
    response_model=SuccessResponseSchema[CategorySchema],
    status_code=status.HTTP_200_OK,
    summary="Частично обновить категорию",
    dependencies=[Depends(get_current_admin)],
)
async def update_category(
    id: int,
    category_data: Annotated[
        UpdateCategorySchema, Depends(UpdateCategorySchema.as_form)
    ],
    services: Annotated[CategoryServices, Depends(get_categories_services)],
):
    """
    Частично обновить категорию по идентификатору.

    - **id** (path): числовой идентификатор категории.
    - **Тело запроса** (JSON): поля, которые нужно обновить (схема `UpdateCategorySchema`, все поля опциональны).

    **Возвращает**:
    - `data`: обновлённый объект `CategorySchema`.

    **Возможные ошибки**:
    - `404 Not Found`: категория с указанным `id` не найдена.
    """
    try:
        data = await services.update_category(id, category_data)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{id}",
    tags=["categories"],
    response_model=SuccessResponseSchema[SuccessDeleteSchema],
    status_code=status.HTTP_200_OK,
    summary="Удалить категорию",
    dependencies=[Depends(get_current_admin)],
)
async def delete_category(
    id: int,
    services: Annotated[CategoryServices, Depends(get_categories_services)],
):
    """
    Удалить категорию по идентификатору.

    - **id** (path): числовой идентификатор категории.

    **Возвращает**:
    - `data`: объект `SuccessDelerteCategorySchema`, содержащий информацию об успешном удалении (например, `id` или статус).

    **Возможные ошибки**:
    - `404 Not Found`: категория с указанным `id` не найдена.
    """
    try:
        data = await services.delete_category(id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

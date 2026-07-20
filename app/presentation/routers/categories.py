from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.categories_schemas import (
    CategorySchema,
    CreateCategorySchema,
    SuccessDelereCategorySchema,
    UpdateCategorySchema,
)
from app.application.services.categories_services import CategoryServices
from app.core.success_response_schema import SuccessResponseSchema
from app.presentation.depends.categories_services import get_categories_services

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "/",
    response_model=SuccessResponseSchema[list[CategorySchema]],
    status_code=status.HTTP_200_OK,
    summary="Получить все категории",
)
async def get_all_categories(
    services: CategoryServices = Depends(get_categories_services),
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
    response_model=SuccessResponseSchema[CategorySchema],
    status_code=status.HTTP_200_OK,
    summary="Получить категорию по ID",
)
async def get_category_by_id(
    id: int,
    services: CategoryServices = Depends(get_categories_services),
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
    response_model=SuccessResponseSchema[CategorySchema],
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую категорию",
)
async def create_category(
    category_data: CreateCategorySchema = Depends(CreateCategorySchema.as_form),
    services: CategoryServices = Depends(get_categories_services),
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
    response_model=SuccessResponseSchema[CategorySchema],
    status_code=status.HTTP_200_OK,
    summary="Частично обновить категорию",
)
async def update_category(
    id: int,
    category_data: UpdateCategorySchema = Depends(UpdateCategorySchema.as_form),
    services: CategoryServices = Depends(get_categories_services),
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
    response_model=SuccessResponseSchema[SuccessDelereCategorySchema],
    status_code=status.HTTP_200_OK,
    summary="Удалить категорию",
)
async def delete_category(
    id: int,
    services: CategoryServices = Depends(get_categories_services),
):
    """
    Удалить категорию по идентификатору.

    - **id** (path): числовой идентификатор категории.

    **Возвращает**:
    - `data`: объект `SuccessDelereCategorySchema`, содержащий информацию об успешном удалении (например, `id` или статус).

    **Возможные ошибки**:
    - `404 Not Found`: категория с указанным `id` не найдена.
    """
    try:
        data = await services.delete_category(id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

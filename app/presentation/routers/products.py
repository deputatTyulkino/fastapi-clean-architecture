from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.application.schemas.entities.products_schemas import (
    CreateProductSchema,
    ProductSchema,
    UpdateProductSchema,
)
from app.application.schemas.utils.query_params_schema import QueryParamsSchema
from app.application.schemas.utils.success_delete_schema import SuccessDeleteSchema
from app.application.schemas.utils.success_response_schema import (
    SuccessPaginatedResponseSchema,
    SuccessResponseSchema,
)
from app.application.services.products_services import ProductServices
from app.domain.models.files import FileDomain
from app.domain.models.users import UserDomain
from app.presentation.depends.entities.products_services import get_product_services
from app.presentation.depends.utils.check_file import (
    check_file_extension,
    check_file_extension_for_update,
)
from app.presentation.depends.utils.check_user import get_current_seller
from app.presentation.routers.categories import router as categories_router

router = APIRouter(prefix="/products", tags=["products"])


@router.get(
    "/",
    response_model=SuccessResponseSchema[SuccessPaginatedResponseSchema[ProductSchema]],
    status_code=status.HTTP_200_OK,
    summary="Получение списка продуктов",
)
async def get_all_products(
    query_params: Annotated[QueryParamsSchema, Depends(QueryParamsSchema.as_form)],
    services: Annotated[ProductServices, Depends(get_product_services)],
):
    """
    Получение списка продуктов с пагинацией.

    Принимает параметры запроса (QueryParamsSchema) для настройки
    пагинации, сортировки и фильтрации. В случае ошибки валидации
    возвращает HTTP 404.
    """
    try:
        data = await services.get_all_products(query_params)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{id}",
    response_model=SuccessResponseSchema[ProductSchema],
    status_code=status.HTTP_200_OK,
    summary="Получение продукта по ID",
)
async def get_product_by_id(
    id: int, services: Annotated[ProductServices, Depends(get_product_services)]
):
    """
    Получение информации о конкретном продукте.

    - **id**: идентификатор продукта.
    Возвращает объект продукта. Если продукт не найден – ошибка 404.
    """
    try:
        data = await services.get_product_by_id(id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@categories_router.get(
    "/{category_id}",
    tags=["products"],
    response_model=SuccessResponseSchema[list[ProductSchema]],
    status_code=status.HTTP_200_OK,
    summary="Продукты по категории",
)
async def get_products_by_category(
    category_id: int,
    services: Annotated[ProductServices, Depends(get_product_services)],
):
    """
    Получение продуктов по идентификатору категории.

    - **category_id**: идентификатор категории.
    Если категория не найдена или не содержит продуктов – возвращается 404.
    """
    try:
        data = await services.get_products_by_category(category_id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/",
    response_model=SuccessResponseSchema[ProductSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового продукта",
)
async def create_product(
    file: Annotated[UploadFile, Depends(check_file_extension)],
    product_data: Annotated[CreateProductSchema, Depends(CreateProductSchema.as_form)],
    services: Annotated[ProductServices, Depends(get_product_services)],
    current_user: Annotated[UserDomain, Depends(get_current_seller)],
):
    """
    Создание продукта.

    Принимает данные формы (CreateProductSchema), файл изображения
    и информацию о текущем продавце. Возвращает созданный продукт.
    При ошибке валидации или отсутствии связанных данных – 404.
    """
    try:
        data = await services.create_product(
            product_data,
            FileDomain(content_type=file.content_type, file_object=file),
            cast(int, current_user.id),
        )
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/{id}",
    response_model=SuccessResponseSchema[ProductSchema],
    status_code=status.HTTP_200_OK,
    summary="Обновление продукта",
)
async def update_product(
    id: int,
    file: Annotated[UploadFile | None, Depends(check_file_extension_for_update)],
    product_data: Annotated[UpdateProductSchema, Depends(UpdateProductSchema.as_form)],
    services: Annotated[ProductServices, Depends(get_product_services)],
    current_user: Annotated[UserDomain, Depends(get_current_seller)],
):
    """
    Частичное обновление продукта.

    - **id**: идентификатор продукта.
    - **file**: новый файл изображения (опционально).
    - **product_data**: поля для обновления.
    Доступно только владельцу-продавцу. При отсутствии продукта – 404.
    """
    try:
        image = (
            FileDomain(content_type=file.content_type, file_object=file)
            if file
            else None
        )
        data = await services.update_product(
            id, product_data, image, cast(int, current_user.id)
        )
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{id}",
    response_model=SuccessResponseSchema[SuccessDeleteSchema],
    status_code=status.HTTP_200_OK,
    summary="Удаление продукта",
)
async def delete_product(
    id: int,
    services: Annotated[ProductServices, Depends(get_product_services)],
    current_user: Annotated[UserDomain, Depends(get_current_seller)],
):
    """
    Удаление продукта.

    - **id**: идентификатор удаляемого продукта.
    Удалить может только продавец, создавший продукт. Если продукт не найден – 404.
    """
    try:
        data = await services.delete_product(id, cast(int, current_user.id))
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

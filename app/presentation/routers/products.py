from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.application.schemas.entities.categories_schemas import CategorySchema
from app.application.schemas.entities.products_schemas import (
    CreateProductSchema,
    MainInfoProductSchema,
    ProductSchema,
    UpdateProductSchema,
)
from app.application.schemas.entities.sellers_schemas import SellerProfileSchema
from app.application.schemas.utils.query_params_schema import QueryParamsProductsSchema
from app.application.schemas.utils.success_delete_schema import SuccessDeleteSchema
from app.application.schemas.utils.success_response_schema import (
    SuccessPaginatedResponseSchema,
    SuccessResponseSchema,
)
from app.application.services.categories_services import CategoryServices
from app.application.services.products_services import ProductServices
from app.application.services.sellers_services import SellerServices
from app.domain.models.files import FileDomain
from app.domain.models.users import UserDomain
from app.presentation.depends.entities.categories_services import (
    get_categories_services,
)
from app.presentation.depends.entities.products_services import get_product_services
from app.presentation.depends.entities.sellers_services import get_sellers_services
from app.presentation.depends.utils.check_file import (
    check_file_extension,
    check_file_extension_for_update,
)
from app.presentation.depends.utils.check_user import get_current_seller, require_admin
from app.presentation.routers.reviews import router as reviews_router

router = APIRouter(prefix="/products")
router.include_router(reviews_router)


@router.get(
    "/",
    tags=["products"],
    response_model=SuccessResponseSchema[
        SuccessPaginatedResponseSchema[MainInfoProductSchema]
    ],
    status_code=status.HTTP_200_OK,
    summary="Получение списка продуктов",
)
async def get_all_products(
    query_params: Annotated[
        QueryParamsProductsSchema, Depends(QueryParamsProductsSchema.as_form)
    ],
    services: Annotated[ProductServices, Depends(get_product_services)],
):
    """
    Получение списка продуктов с пагинацией.

    Принимает параметры запроса для настройки
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
    tags=["products"],
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


@router.get(
    "/{id}/category",
    response_model=SuccessResponseSchema[CategorySchema],
    status_code=status.HTTP_200_OK,
    tags=["categories"],
)
async def get_category_by_product(
    id: int, services: Annotated[CategoryServices, Depends(get_categories_services)]
):
    try:
        data = await services.get_category_by_product(id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{id}/seller",
    response_model=SuccessResponseSchema[SellerProfileSchema],
    status_code=status.HTTP_200_OK,
    tags=["sellers"],
)
async def get_seller_by_id(
    id: int, services: Annotated[SellerServices, Depends(get_sellers_services)]
):
    try:
        data = await services.get_seller_by_product(id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/",
    tags=["products"],
    response_model=SuccessResponseSchema[ProductSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового продукта",
)
async def create_product(
    image: Annotated[UploadFile, Depends(check_file_extension)],
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
            FileDomain(content_type=image.content_type, file_object=image),
            cast(int, current_user.id),
        )
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/{id}",
    tags=["products"],
    response_model=SuccessResponseSchema[ProductSchema],
    status_code=status.HTTP_200_OK,
    summary="Обновление продукта",
)
async def update_product(
    id: int,
    image: Annotated[UploadFile | None, Depends(check_file_extension_for_update)],
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
        new_image = (
            FileDomain(content_type=image.content_type, file_object=image)
            if image
            else None
        )
        data = await services.update_product(
            id, product_data, new_image, cast(int, current_user.id)
        )
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{id}",
    tags=["products"],
    response_model=SuccessResponseSchema[SuccessDeleteSchema],
    status_code=status.HTTP_200_OK,
    summary="Удаление продукта",
    dependencies=[Depends(require_admin)],
)
async def delete_product(
    id: int,
    services: Annotated[ProductServices, Depends(get_product_services)],
    current_user: Annotated[UserDomain, Depends(get_current_seller)],
):
    """
    Удаление продукта.

    - **id**: идентификатор удаляемого продукта.
    Удалить может только продавец, создавший продукт или админ. Если продукт не найден – 404.
    """
    try:
        data = await services.delete_product(
            id, cast(int, current_user.id), current_user.is_admin
        )
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

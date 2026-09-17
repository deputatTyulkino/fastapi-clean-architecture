from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.entities.cart_items_schemas import (
    CartItemSchema,
    CreateCartItemSchema,
)
from app.application.schemas.utils.success_response_schema import SuccessResponseSchema
from app.application.services.cart_items_services import CartItemsServices
from app.domain.models.users import UserDomain
from app.presentation.depends.entities.cart_items_services import (
    get_cart_items_services,
)
from app.presentation.depends.utils.check_user import get_current_user

router = APIRouter(prefix="/cart_items", tags=["cart_items"])


@router.get(
    "/",
    response_model=SuccessResponseSchema[list[CartItemSchema]],
    status_code=status.HTTP_200_OK,
)
async def get_all_cart_items(
    services: Annotated[CartItemsServices, Depends(get_cart_items_services)],
    user: Annotated[UserDomain, Depends(get_current_user)],
):
    try:
        data = await services.get_all_cart_items(cast(int, user.id))
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.H404, detail=str(e))


@router.post(
    "/",
    response_model=SuccessResponseSchema[CartItemSchema],
    status_code=status.HTTP_201_CREATED,
)
async def create_cart_item(
    services: Annotated[CartItemsServices, Depends(get_cart_items_services)],
    cart_item_data: Annotated[
        CreateCartItemSchema, Depends(CreateCartItemSchema.as_form)
    ],
    user: Annotated[UserDomain, Depends(get_current_user)],
):
    try:
        data = await services.create_cart_item(cast(int, user.id), cart_item_data)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/{product_id}",
    response_model=SuccessResponseSchema[CartItemSchema],
    status_code=status.HTTP_200_OK,
)
async def update_cart_item(
    product_id: int,
    services: Annotated[CartItemsServices, Depends(get_cart_items_services)],
    user: Annotated[UserDomain, Depends(get_current_user)],
):
    try:
        data = await services.update_cart_item(cast(int, user.id), product_id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{product_id}",
    response_model=SuccessResponseSchema[CartItemSchema],
    status_code=status.HTTP_200_OK,
)
async def delete_cart_item(
    product_id: int,
    services: Annotated[CartItemsServices, Depends(get_cart_items_services)],
    user: Annotated[UserDomain, Depends(get_current_user)],
):
    try:
        data = await services.delete_cart_item(cast(int, user.id), product_id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

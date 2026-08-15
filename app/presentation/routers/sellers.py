from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.application.schemas.entities.sellers_schemas import (
    CreateSellerProfileSchema,
    SellerProfileSchema,
    UpdateSellerProfileSchema,
)
from app.application.schemas.utils.success_delete_schema import SuccessDeleteSchema
from app.application.schemas.utils.success_response_schema import SuccessResponseSchema
from app.application.services.sellers_services import SellerServices
from app.domain.models.files import FileDomain
from app.presentation.depends.entities.sellers_services import get_sellers_services

router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.get(
    "/{id}",
    response_model=SuccessResponseSchema[SellerProfileSchema],
    status_code=status.HTTP_200_OK,
)
async def get_seller_profile_by_id(
    id: int, services: Annotated[SellerServices, Depends(get_sellers_services)]
):
    try:
        data = await services.get_seller_by_id(id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/",
    response_model=SuccessResponseSchema[SellerProfileSchema],
    status_code=status.HTTP_201_CREATED,
)
async def create_seller_profile(
    seller_data: Annotated[
        CreateSellerProfileSchema, Depends(CreateSellerProfileSchema.as_form)
    ],
    logo: UploadFile | None,
    banner: UploadFile | None,
    services: Annotated[SellerServices, Depends(get_sellers_services)],
):
    try:
        new_logo = (
            FileDomain(content_type=logo.content_type, file_object=logo)
            if logo
            else None
        )
        new_banner = (
            FileDomain(content_type=banner.content_type, file_object=banner)
            if banner
            else None
        )
        data = await services.create_seller(new_logo, new_banner, seller_data)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/{id}",
    response_model=SuccessResponseSchema[SellerProfileSchema],
    status_code=status.HTTP_200_OK,
)
async def update_seller_profile(
    id: int,
    logo: UploadFile | None,
    banner: UploadFile | None,
    seller_data: Annotated[
        UpdateSellerProfileSchema, Depends(UpdateSellerProfileSchema.as_form)
    ],
    services: Annotated[SellerServices, Depends(get_sellers_services)],
):
    try:
        new_logo = (
            FileDomain(content_type=logo.content_type, file_object=logo)
            if logo
            else None
        )
        new_banner = (
            FileDomain(content_type=banner.content_type, file_object=banner)
            if banner
            else None
        )
        data = await services.update_seller(id, new_logo, new_banner, seller_data)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{id}",
    response_model=SuccessResponseSchema[SuccessDeleteSchema],
    status_code=status.HTTP_200_OK,
)
async def delete_seller_profile(
    id: int, services: Annotated[SellerServices, Depends(get_sellers_services)]
):
    try:
        data = await services.delete_seller(id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.entities.reviews_schemas import (
    CreateReviewSchema,
    ReviewSchema,
    UpdateReviewSchema,
)
from app.application.schemas.utils.query_params_schema import ParamsReviewsSchema
from app.application.schemas.utils.success_delete_schema import SuccessDeleteSchema
from app.application.schemas.utils.success_response_schema import SuccessResponseSchema
from app.application.services.reviews_services import ReviewServices
from app.domain.models.users import UserDomain
from app.presentation.depends.entities.reviews_services import get_reviews_services
from app.presentation.depends.utils.check_user import get_current_user, require_admin

router = APIRouter(prefix="/{product_id}/reviews")


@router.get(
    "/",
    response_model=SuccessResponseSchema[list[ReviewSchema]],
    status_code=status.HTTP_200_OK,
    tags=["reviews"],
)
async def get_reviews(
    query_params: Annotated[ParamsReviewsSchema, Depends(ParamsReviewsSchema.as_form)],
    services: Annotated[ReviewServices, Depends(get_reviews_services)],
):
    try:
        data = await services.get_all_reviews(query_params)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/top",
    response_model=SuccessResponseSchema[list[ReviewSchema]],
    status_code=status.HTTP_200_OK,
    tags=["reviews"],
)
async def get_top_reviews(
    product_id: int, services: Annotated[ReviewServices, Depends(get_reviews_services)]
):
    try:
        data = await services.get_top_reviews(product_id)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/",
    response_model=SuccessResponseSchema[ReviewSchema],
    status_code=status.HTTP_201_CREATED,
    tags=["reviews"],
)
async def create_review(
    review_data: Annotated[CreateReviewSchema, Depends(CreateReviewSchema.as_form)],
    services: Annotated[ReviewServices, Depends(get_reviews_services)],
    user: Annotated[UserDomain, Depends(get_current_user)],
):
    try:
        data = await services.create_review(review_data, cast(int, user.id))
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/{id}",
    response_model=SuccessResponseSchema[ReviewSchema],
    status_code=status.HTTP_200_OK,
    tags=["reviews"],
)
async def update_review(
    id: int,
    review_data: Annotated[UpdateReviewSchema, Depends(UpdateReviewSchema.as_form)],
    services: Annotated[ReviewServices, Depends(get_reviews_services)],
    user: Annotated[UserDomain, Depends(get_current_user)],
):
    try:
        data = await services.update_review(id, review_data, cast(int, user.id))
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{id}",
    response_model=SuccessResponseSchema[SuccessDeleteSchema],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
    tags=["reviews"],
)
async def delete_review(
    id: int,
    services: Annotated[ReviewServices, Depends(get_reviews_services)],
    user: Annotated[UserDomain, Depends(get_current_user)],
):
    try:
        data = await services.delete_review(id, cast(int, user.id), user.is_admin)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

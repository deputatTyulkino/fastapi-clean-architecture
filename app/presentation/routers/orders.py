from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.application.schemas.entities.orders_schemas import (
    OrderResponseSchema,
    OrderStatusResponse,
)
from app.application.schemas.utils.query_params_schema import OrdersParamsSchema
from app.application.schemas.utils.success_response_schema import SuccessResponseSchema
from app.application.services.orders_services import OrdersServices
from app.domain.interfaces.utils.i_payment_repo import IPaymentWebhookRequest
from app.domain.models.users import UserDomain
from app.presentation.depends.entities.orders_services import get_orders_services
from app.presentation.depends.utils.check_user import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get(
    "/",
    response_model=SuccessResponseSchema[list[OrderResponseSchema]],
    status_code=status.HTTP_200_OK,
)
async def get_all_orders(
    services: Annotated[OrdersServices, Depends(get_orders_services)],
    user: Annotated[UserDomain, Depends(get_current_user)],
    query_params: Annotated[OrdersParamsSchema, Depends(OrdersParamsSchema.as_form)],
):
    try:
        data = await services.get_all_orders(cast(int, user.id), query_params)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{order_id}",
    response_model=SuccessResponseSchema[OrderResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_order(
    order_id: int,
    services: Annotated[OrdersServices, Depends(get_orders_services)],
    user: Annotated[UserDomain, Depends(get_current_user)],
):
    try:
        data = await services.get_order(order_id, cast(int, user.id))
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/",
    response_model=SuccessResponseSchema[OrderResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
async def checkout_order(
    services: Annotated[OrdersServices, Depends(get_orders_services)],
    user: Annotated[UserDomain, Depends(get_current_user)],
):
    try:
        data = await services.create_order(cast(int, user.id))
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{order_id}/status",
    response_model=SuccessResponseSchema[OrderStatusResponse],
    status_code=status.HTTP_200_OK,
)
async def get_order_status(
    order_id: int,
    services: Annotated[OrdersServices, Depends(get_orders_services)],
    user: Annotated[UserDomain, Depends(get_current_user)],
):
    try:
        data = await services.get_order_status(order_id, cast(int, user.id))
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def accept_payment(
    request: Request,
    services: Annotated[OrdersServices, Depends(get_orders_services)],
    payment_data: IPaymentWebhookRequest,
):
    client_ip = None
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    client_ip = request.client.host if request.client else None
    data = await services.res_accept_payment(client_ip, payment_data)
    return JSONResponse(data)

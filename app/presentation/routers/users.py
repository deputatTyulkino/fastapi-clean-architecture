from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from app.application.schemas.entities.users_schemas import (
    LoginUserSchema,
    RegisterUserSchema,
    ResponseUserSchema,
    VerifyUserEmailSchema,
)
from app.application.schemas.utils.success_response_schema import SuccessResponseSchema
from app.application.services.users_services import UserServices
from app.domain.interfaces.utils.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    ValidationError,
)
from app.infrastructure.depends.utils.exceptions import (
    ConflictHTTPError,
    ForbiddenHTTPError,
    UnprocessableEntityHTTPError,
)
from app.presentation.depends.entities.users_services import get_users_servcies

router = APIRouter(prefix="/auth", tags=["users"])


@router.post(
    "/register",
    response_model=SuccessResponseSchema[ResponseUserSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register_user(
    user_data: Annotated[RegisterUserSchema, Depends(RegisterUserSchema.as_form)],
    services: Annotated[UserServices, Depends(get_users_servcies)],
):
    try:
        data = await services.register_user(user_data)
        return SuccessResponseSchema(data=ResponseUserSchema.model_validate(data))
    except UserAlreadyExistsError:
        raise ConflictHTTPError()


@router.post(
    "/verify",
    response_model=SuccessResponseSchema[ResponseUserSchema],
    status_code=status.HTTP_201_CREATED,
)
async def verify_user(
    response: Response,
    user_data: Annotated[VerifyUserEmailSchema, Depends(VerifyUserEmailSchema.as_form)],
    services: Annotated[UserServices, Depends(get_users_servcies)],
):
    try:
        data = await services.verify_user_email(user_data)
        response.set_cookie(
            key="refresh_token",
            value=data.refresh,
            samesite="strict",
            httponly=True,
            secure=False,  # prod: True
            path="/auth",
            max_age=60 * 60 * 24 * 30,
        )
        return SuccessResponseSchema(data=ResponseUserSchema.model_validate(data))
    except AuthenticationError:
        raise ForbiddenHTTPError()
    except ValidationError:
        raise UnprocessableEntityHTTPError()


@router.post(
    "/login",
    response_model=SuccessResponseSchema[ResponseUserSchema],
    status_code=status.HTTP_200_OK,
    summary="Аутентификация пользователя",
)
async def login_user(
    response: Response,
    user_data: Annotated[LoginUserSchema, Depends(LoginUserSchema.as_form)],
    services: Annotated[UserServices, Depends(get_users_servcies)],
):
    try:
        data = await services.login_user(user_data)
        response.set_cookie(
            key="refresh_token",
            value=data.refresh,
            samesite="strict",
            httponly=True,
            secure=False,  # prod: True
            path="/auth",
            max_age=60 * 60 * 24 * 30,
        )
        return SuccessResponseSchema(data=ResponseUserSchema.model_validate(data))
    except AuthenticationError:
        raise ForbiddenHTTPError()


@router.post(
    "/refresh",
    response_model=SuccessResponseSchema[ResponseUserSchema],
    status_code=status.HTTP_200_OK,
    summary="Обновление токенов",
)
async def refresh_token(
    response: Response,
    services: Annotated[UserServices, Depends(get_users_servcies)],
    refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None,
):
    if refresh_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Авторизуйтесь снова")
    try:
        data = await services.refresh_token(refresh_token)
    except AuthenticationError:
        response.delete_cookie("refresh_token", path="/auth")
        raise ForbiddenHTTPError()
    return SuccessResponseSchema(data=ResponseUserSchema.model_validate(data))


@router.post(
    "/logout", response_model=SuccessResponseSchema[str], status_code=status.HTTP_200_OK
)
async def logout(
    response: Response,
    services: Annotated[UserServices, Depends(get_users_servcies)],
    refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None,
):
    if refresh_token:
        await services.logout(refresh_token)
    response.delete_cookie("refresh_token", path="/auth")

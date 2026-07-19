from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.users_schemas import (
    LoginUserSchema,
    RefreshTokenSchema,
    RegisterUserSchema,
    ResponseUserSchema,
)
from app.application.services.users_services import UserServices
from app.core.success_response_schema import SuccessResponseSchema
from app.presentation.depends.users_services import get_users_servcies

router = APIRouter(prefix="/auth", tags=["users"])


@router.post(
    "/register",
    response_model=SuccessResponseSchema[ResponseUserSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создаёт учётную запись с переданными данными и возвращает информацию о пользователе.",
)
async def register_user(
    user_data: RegisterUserSchema = Depends(RegisterUserSchema.as_form),
    services: UserServices = Depends(get_users_servcies),
):
    """
    Регистрация нового пользователя.

    Принимает данные формы,
    создаёт пользователя через сервисный слой и возвращает объект с информацией о созданном пользователе.
    """
    try:
        data = await services.register_user(user_data)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/login",
    response_model=SuccessResponseSchema[ResponseUserSchema],
    status_code=status.HTTP_200_OK,
    summary="Аутентификация пользователя",
    description="Проверяет учётные данные и возвращает токены доступа и обновления.",
)
async def login_user(
    user_data: LoginUserSchema = Depends(LoginUserSchema.as_form),
    services: UserServices = Depends(get_users_servcies),
):
    """
    Вход пользователя в систему.

    Ожидает тело запроса с учётными данными.
    При успешной проверке возвращает информацию о пользователе вместе с токенами.
    """
    try:
        data = await services.login_user(user_data)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/refresh",
    response_model=SuccessResponseSchema[ResponseUserSchema],
    status_code=status.HTTP_200_OK,
    summary="Обновление токенов",
    description="Принимает refresh-токен и возвращает новую пару access/refresh токенов.",
)
async def refresh_token(
    refresh_dict_info: RefreshTokenSchema = Depends(RefreshTokenSchema.as_form),
    services: UserServices = Depends(get_users_servcies),
):
    """
    Обновление пары токенов.

    Использует переданный refresh-токен для выдачи нового access-токена
    и refresh-токена, возвращает обновлённую информацию о пользователе.
    """
    try:
        data = await services.refresh_token(refresh_dict_info)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

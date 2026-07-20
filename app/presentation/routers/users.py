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
)
async def register_user(
    user_data: RegisterUserSchema = Depends(RegisterUserSchema.as_form),
    services: UserServices = Depends(get_users_servcies),
):
    """
    Регистрация нового пользователя.

    **Параметры запроса** (form-data):
    - Все поля, определённые в `RegisterUserSchema` (обычно `email`, `password`, `username` и т.д.).

    **Возвращает**:
    - `data`: объект `ResponseUserSchema` с информацией о созданном пользователе (включая `id`, `email`, `username` и, возможно, токены).

    **Возможные ошибки**:
    - `409 Conflict`: пользователь с таким email/username уже существует.
    - `400 Bad Request`: неверный формат данных (например, слабый пароль, некорректный email) — если такая валидация есть в сервисе.
    """
    try:
        data = await services.register_user(user_data)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        # В зависимости от логики сервиса может быть 409 или 400
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/login",
    response_model=SuccessResponseSchema[ResponseUserSchema],
    status_code=status.HTTP_200_OK,
    summary="Аутентификация пользователя",
)
async def login_user(
    user_data: LoginUserSchema = Depends(LoginUserSchema.as_form),
    services: UserServices = Depends(get_users_servcies),
):
    """
    Вход пользователя в систему.

    **Параметры запроса** (form-data):
    - Поля из `LoginUserSchema` (обычно `email`/`username` и `password`).

    **Возвращает**:
    - `data`: объект `ResponseUserSchema`, содержащий информацию о пользователе и пару токенов (access, refresh).

    **Возможные ошибки**:
    - `400 Bad Request`: неверные учётные данные (пользователь не найден или пароль не совпадает).
    - `409 Conflict` / `403 Forbidden`: если учётная запись заблокирована или требует подтверждения (зависит от бизнес-логики).
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
)
async def refresh_token(
    refresh_dict_info: RefreshTokenSchema = Depends(RefreshTokenSchema.as_form),
    services: UserServices = Depends(get_users_servcies),
):
    """
    Обновление пары токенов.

    **Параметры запроса** (form-data):
    - `refresh_token` (строка, обязательное) — действующий refresh-токен.

    **Возвращает**:
    - `data`: объект `ResponseUserSchema` с обновлёнными токенами (access, refresh) и данными пользователя.

    **Возможные ошибки**:
    - `400 Bad Request`: передан невалидный, истёкший или отсутствующий refresh-токен.
    - `401 Unauthorized`: токен недействителен (если сервис выбрасывает более специфичное исключение, можно заменить статус).
    """
    try:
        data = await services.refresh_token(refresh_dict_info)
        return SuccessResponseSchema(data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

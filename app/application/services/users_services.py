from app.application.schemas.entities.users_schemas import (
    LoginUserSchema,
    RefreshTokenSchema,
    RegisterUserSchema,
    ResponseUserSchema,
    UserSchema,
)
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.interfaces.utils.i_token_services import ITokenServices
from app.domain.models.users import UserDomain


class UserServices:
    def __init__(self, uow: IUnitOfWork, token_services: ITokenServices):
        self.uow = uow
        self.token_services = token_services

    async def register_user(self, user_data: RegisterUserSchema) -> ResponseUserSchema:
        async with self.uow as uow:
            user = await uow.users.get_by_email(user_data.email)
            if user:
                raise ValueError(f"Пользователь с {user.email} уже существует")
            user = await uow.users.create(
                UserDomain(
                    email=user_data.email,
                    hashed_password=self.token_services.hash_password(
                        user_data.password
                    ),
                )
            )
            await uow.commit()
        data_info = {"sub": user.email, "role": user.role, "id": user.id}
        data = {
            "user": UserSchema.model_validate(user),
            "access": self.token_services.create_token(data_info, "access"),
            "refresh": self.token_services.create_token(data_info, "refresh"),
        }
        return ResponseUserSchema.model_validate(data)

    async def login_user(self, user_data: LoginUserSchema) -> ResponseUserSchema:
        async with self.uow as uow:
            user = await uow.users.get_by_email(user_data.email)
            if (
                not user
                or not user.is_active
                or not self.token_services.verify_password(
                    user_data.password, user.hashed_password
                )
            ):
                raise ValueError("Неправильный email или пароль")
        data_info = {"sub": user.email, "role": user.role, "id": user.id}
        data = {
            "user": UserSchema.model_validate(user),
            "access": self.token_services.create_token(data_info, "access"),
            "refresh": self.token_services.create_token(data_info, "refresh"),
        }
        return ResponseUserSchema.model_validate(data)

    async def refresh_token(
        self, refresh_dict_info: RefreshTokenSchema
    ) -> ResponseUserSchema:
        message = "Не получилось обновить сессию, авторизуйтесь снова"
        payload = self.token_services.decode_token(refresh_dict_info.refresh)
        if payload is None:
            raise ValueError(message)
        if payload.get("email") is None or payload.get("token_type") != "refresh":
            raise ValueError(message)
        async with self.uow as uow:
            user = await uow.users.get_by_email(payload["email"])
            if not user or not user.is_active:
                raise ValueError(message)
        data_info = {"sub": user.email, "role": user.role, "id": user.id}
        data = {
            "user": UserSchema.model_validate(user),
            "access": self.token_services.create_token(data_info, "access"),
            "refresh": self.token_services.create_token(data_info, "refresh"),
        }
        return ResponseUserSchema.model_validate(data)

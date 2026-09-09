import uuid
from typing import cast

from app.application.schemas.entities.users_schemas import (
    AuthResult,
    LoginUserSchema,
    RegisterUserSchema,
    UserSchema,
)
from app.domain.interfaces.auth.i_refresh_token_repo import IRefreshTokenRepo
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.interfaces.utils.i_token_services import ITokenServices
from app.domain.models.users import UserDomain


class UserServices:
    def __init__(
        self,
        uow: IUnitOfWork,
        token_services: ITokenServices,
        refresh_token_repo: IRefreshTokenRepo,
    ):
        self.uow = uow
        self.token_services = token_services
        self.refresh_token_repo = refresh_token_repo

    async def _create_tokens(self, user: UserDomain, family_id: str) -> tuple[str, str]:
        access = self.token_services.create_access_token(
            {"sub": user.email, "role": user.role, "id": user.id}
        )
        refresh = self.token_services.create_refresh_token()
        refresh_hash = self.token_services.hash_refresh_token(refresh)
        await self.refresh_token_repo.create(
            refresh_hash, cast(int, user.id), family_id
        )
        return access, refresh

    async def register_user(self, user_data: RegisterUserSchema) -> AuthResult:
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
        family_id = str(uuid.uuid4())
        access, refresh = await self._create_tokens(user, family_id)
        return AuthResult(
            user=UserSchema.model_validate(user), access=access, refresh=refresh
        )

    async def login_user(self, user_data: LoginUserSchema) -> AuthResult:
        async with self.uow as uow:
            user = await uow.users.get_by_email(user_data.email)
            if user is None or not self.token_services.verify_password(
                user_data.password, user.hashed_password
            ):
                raise ValueError("Неправильный email или пароль")
            if not user.is_active:
                raise ValueError("Пользователь не активен")
        family_id = str(uuid.uuid4())
        access, refresh = await self._create_tokens(user, family_id)
        return AuthResult(
            user=UserSchema.model_validate(user), access=access, refresh=refresh
        )

    async def refresh_token(self, refresh_token: str) -> AuthResult:
        message = "Не получилось обновить сессию, авторизуйтесь снова"
        old_refresh_hash = self.token_services.hash_refresh_token(refresh_token)
        record = await self.refresh_token_repo.get(old_refresh_hash)
        if record is None:
            raise ValueError(message)
        async with self.uow as uow:
            user = await uow.users.get_by_email(record["user_id"])
            if not user or not user.is_active:
                await self.refresh_token_repo.revoke_family(record["family_id"])
                raise ValueError(message)
        access = self.token_services.create_access_token(
            {"sub": user.email, "role": user.role, "id": user.id}
        )
        new_refresh = self.token_services.create_refresh_token()
        new_refresh_hash = self.token_services.hash_refresh_token(new_refresh)
        await self.refresh_token_repo.rotate(
            old_refresh_hash, new_refresh_hash, cast(int, user.id), record["family_id"]
        )
        return AuthResult(
            user=UserSchema.model_validate(user), access=access, refresh=new_refresh
        )

    async def logout(self, refresh: str) -> None:
        token_hash = self.token_services.hash_refresh_token(refresh)
        record = await self.refresh_token_repo.get(token_hash)
        if record:
            await self.refresh_token_repo.revoke_family(record["family_id"])

import hashlib
import uuid
from typing import cast

from dns import ttl

from app.application.schemas.entities.users_schemas import (
    AuthResult,
    LoginUserSchema,
    RegisterResponseSchema,
    RegisterUserSchema,
    UserSchema,
    VerifyUserEmailSchema,
)
from app.domain.interfaces.auth.i_refresh_token_repo import IRefreshTokenRepo
from app.domain.interfaces.mail.i_mail_manager import IMailManager
from app.domain.interfaces.redis.i_serializer_services import ISerializerServices
from app.domain.interfaces.redis.i_state_client import IStateClient
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.interfaces.utils.i_token_services import ITokenServices
from app.domain.models.users import UserDomain
from app.infrastructure.celery.tasks.mail_tasks import verify_mail_task


class UserServices:
    def __init__(
        self,
        uow: IUnitOfWork,
        token_services: ITokenServices,
        refresh_token_repo: IRefreshTokenRepo,
        mail_manager: IMailManager,
        state_client: IStateClient,
        serializer_services: ISerializerServices,
    ):
        self.uow = uow
        self.token_services = token_services
        self.refresh_token_repo = refresh_token_repo
        self.mail_manager = mail_manager
        self.state_client = state_client
        self.serializer_services = serializer_services

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

    async def verify_user_email(
        self, verify_user_data: VerifyUserEmailSchema
    ) -> AuthResult:
        key = f"verify:user:{verify_user_data.user_code}"
        serialized_user_data = await self.state_client.get(key)
        if serialized_user_data is None:
            raise ValueError("Действие кода закончилось")
        user_data = self.serializer_services.deserializer(serialized_user_data)
        if user_data is None:
            raise ValueError("Ошибка сериализации")
        attempts = user_data["attempts"]
        if attempts >= 5:
            raise ValueError("Превышено количество попыток")
        code = user_data["code"]
        if code != hashlib.sha256(verify_user_data.code.encode()).hexdigest():
            user_data["attempts"] += 1
            await self.state_client.set(
                key,
                cast(str, self.serializer_services.serializer(user_data)),
                ttl=600,  # лучше добавить keepttl
            )
            raise ValueError("Неверный код")
        async with self.uow as uow:
            user = await uow.users.create(
                UserDomain(
                    email=user_data["email"], hashed_password=user_data["password"]
                )
            )
            await uow.commit()
        family_id = str(uuid.uuid4())
        access, refresh = await self._create_tokens(user, family_id)
        return AuthResult(
            user=UserSchema.model_validate(user), access=access, refresh=refresh
        )

    async def register_user(
        self, user_data: RegisterUserSchema
    ) -> RegisterResponseSchema:
        async with self.uow as uow:
            user = await uow.users.get_by_email(user_data.email)
            if user:
                raise ValueError(f"Пользователь с {user.email} уже существует")
        user_verify_code = str(uuid.uuid4())
        code = self.mail_manager.generate_verification_code()
        hash_code = hashlib.sha256(code.encode()).hexdigest()
        await self.state_client.set(
            f"verify:user:{user_verify_code}",
            cast(
                str,
                self.serializer_services.serializer(
                    {
                        "email": user_data.email,
                        "code": hash_code,
                        "password": user_data.password,
                        "attempts": 0,
                    }
                ),
            ),
            ttl=600,
        )
        verify_mail_task.delay(user_data.email, code)
        return RegisterResponseSchema(user_code=user_verify_code)

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
            user = await uow.users.get_by_id(record["user_id"])
            if user is None or not user.is_active:
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
        record = await self.refresh_token_repo.get(
            self.token_services.hash_refresh_token(refresh)
        )
        if record:
            await self.refresh_token_repo.revoke_family(record["family_id"])

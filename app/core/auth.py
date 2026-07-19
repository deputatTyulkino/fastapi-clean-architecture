from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.infrastructure.database.depends import get_db
from app.infrastructure.models.users import UserORM

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class Security:
    def __init__(self, settings: Settings):
        self.settings = settings

    def decode_token(self, token) -> dict | None:
        try:
            payload = jwt.decode(
                token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM]
            )
            return {
                "email": payload["sub"],
                "token_type": payload["token_type"],
            }
        except jwt.ExpiredSignatureError:
            return None
        except jwt.PyJWTError:
            return None

    def hash_password(self, password: str) -> str:
        """
        Преобразует пароль в хеш с использованием bcrypt.
        """
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Проверяет, соответствует ли введённый пароль сохранённому хешу.
        """
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict):
        """
        Создаёт JWT с payload (sub, role, id, exp).
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire, "token_type": "access"})
        return jwt.encode(
            to_encode, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )

    def create_refresh_token(self, data: dict):
        """
        Создаёт refresh-токен с длительным сроком действия и token_type="refresh".
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update({"exp": expire, "token_type": "refresh"})
        return jwt.encode(
            to_encode, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
    ):
        """
        Проверяет JWT и возвращает пользователя из базы.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM]
            )
            email: str | None = payload.get("sub")
            token_type: str | None = payload.get("token_type")
            if email is None or token_type != "access":
                raise credentials_exception
        except jwt.InvalidTokenError:
            raise credentials_exception
        result = await db.scalars(
            select(UserORM).where(UserORM.email == email, UserORM.is_active)
        )
        user = result.first()
        if user is None:
            raise credentials_exception
        return user

    async def get_current_seller(
        self, current_user: UserORM = Depends(get_current_user)
    ):
        """
        Проверяет, что пользователь имеет роль 'seller'.
        """
        if current_user.role != "seller":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only sellers can perform this action",
            )
        return current_user

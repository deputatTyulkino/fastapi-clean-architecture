import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import Settings
from app.domain.interfaces.utils.i_token_services import ITokenServices


class TokenServices(ITokenServices):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def decode_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM]
            )
            return {
                "email": payload["sub"],
                "token_type": payload["token_type"],
            }
        except jwt.PyJWTError:
            return None

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {**data, "exp": expire, "token_type": "access"}
        return jwt.encode(
            to_encode, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )

    @staticmethod
    def create_refresh_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_refresh_token(token_raw: str) -> str:
        return hashlib.sha256(token_raw.encode()).hexdigest()

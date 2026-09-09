from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    DATABASE_URL: str
    YOOKASSA_SHOP_ID: int
    YOOKASSA_SECRET_KEY: str
    YOOKASSA_RETURN_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REDIS_VOLATILE_URL: str
    REDIS_DURABLE_URL: str
    REFRESH_COOKIE_NAME: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return Settings()  # pyright: ignore

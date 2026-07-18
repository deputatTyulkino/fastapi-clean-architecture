import re
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class ResponseUserSchema(BaseModel):
    user: UserSchema
    access: str
    refresh: str


class LoginUserSchema(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль", min_length=8)


class RegisterUserSchema(LoginUserSchema):
    password_confirm: str

    @field_validator("password")
    @classmethod
    def password_validator(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Пароль должен содержать заглавные буквы")
        if not re.search(r"\d", value):
            raise ValueError("Пароль должен содержать цифры")
        if not re.search(r"[a-z]", value):
            raise ValueError("Пароль должен содержать строчные буквы")
        return value

    @model_validator(mode="after")
    def check_equal_passwords(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError("Пароли не совпадают")
        return self


class RefreshTokenSchema(BaseModel):
    refresh: str

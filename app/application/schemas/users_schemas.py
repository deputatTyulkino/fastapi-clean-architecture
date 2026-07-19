import re
from typing import Annotated, Self

from fastapi import Form
from fastapi.exceptions import RequestValidationError
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationError,
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

    @classmethod
    def as_form(
        cls,
        email: Annotated[EmailStr, Form(...)],
        password: Annotated[str, Form(...)],
    ):
        try:
            return cls(email=email, password=password)
        except ValidationError as e:
            raise RequestValidationError(e.errors())


class RegisterUserSchema(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль", min_length=8)
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

    @classmethod
    def as_form(
        cls,
        email: Annotated[EmailStr, Form(...)],
        password: Annotated[str, Form(...)],
        password_confirm: Annotated[str, Form(...)],
    ):
        try:
            return cls(
                email=email, password=password, password_confirm=password_confirm
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())


class RefreshTokenSchema(BaseModel):
    refresh: str

    @classmethod
    def as_form(
        cls,
        refresh: Annotated[str, Form(...)],
    ):
        try:
            return cls(refresh=refresh)
        except ValidationError as e:
            raise RequestValidationError(e.errors())

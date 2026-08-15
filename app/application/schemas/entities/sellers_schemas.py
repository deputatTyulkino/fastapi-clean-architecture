from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Form
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.application.schemas.entities.users_schemas import UserSchema


class SellerProfileSchema(BaseModel):
    id: int
    store_name: str
    rating: Decimal
    description: str | None
    logo_url: str | None
    banner_url: str | None
    legal_name: str | None
    tax_id: str | None
    phone: str | None
    status: str
    reviews_count: int
    created_at: datetime
    updated_at: datetime
    user: UserSchema
    model_config = ConfigDict(from_attributes=True)


class CreateSellerProfileSchema(BaseModel):
    user_id: int = Field(
        ..., description="ID пользователя, к которому привязан аккаунт продаца", ge=0
    )
    description: str | None = Field(description="Описание", min_length=3)
    store_name: str = Field(..., description="Название", min_length=3)
    legal_name: str | None = Field(description="Название по документам")
    tax_id: str | None
    phone: str | None = Field(description="Номер для свзяи")

    @classmethod
    def as_form(
        cls,
        user_id: Annotated[int, Form(...)],
        store_name: Annotated[str, Form(...)],
        legal_name: Annotated[str | None, Form()] = None,
        description: Annotated[str | None, Form()] = None,
        tax_id: Annotated[str | None, Form()] = None,
        phone: Annotated[str | None, Form()] = None,
    ):
        try:
            return cls(
                user_id=user_id,
                store_name=store_name,
                legal_name=legal_name,
                description=description,
                tax_id=tax_id,
                phone=phone,
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())


class UpdateSellerProfileSchema(BaseModel):
    description: str | None = Field(description="Описание", min_length=3)
    store_name: str | None = Field(description="Название", min_length=3)
    legal_name: str | None = Field(description="Название по документам")
    tax_id: str | None = Field(min_length=3)
    phone: str | None = Field(description="Номер для свзяи")

    @classmethod
    def as_form(
        cls,
        store_name: Annotated[str | None, Form()] = None,
        legal_name: Annotated[str | None, Form()] = None,
        description: Annotated[str | None, Form()] = None,
        tax_id: Annotated[str | None, Form()] = None,
        phone: Annotated[str | None, Form()] = None,
    ):
        try:
            return cls(
                store_name=store_name,
                legal_name=legal_name,
                description=description,
                tax_id=tax_id,
                phone=phone,
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())

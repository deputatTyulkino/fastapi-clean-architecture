from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Form
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class MainInfoProductSchema(BaseModel):
    id: int
    name: str
    price: Decimal
    image_url: str
    rating: Decimal
    model_config = ConfigDict(from_attributes=True)


class ProductSchema(MainInfoProductSchema):
    description: str
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category_id: int
    seller_id: int
    model_config = ConfigDict(from_attributes=True)


class CreateProductSchema(BaseModel):
    name: str = Field(..., description="Имя продукта", min_length=3)
    description: str = Field(..., description="Описание продукта", min_length=3)
    price: Decimal = Field(..., description="Цена продукта", ge=1)
    stock: int = Field(..., description="Количество продуктов", ge=0)
    category_id: int = Field(..., description="ID категории", ge=0)

    @classmethod
    def as_form(
        cls,
        name: Annotated[str, Form(...)],
        description: Annotated[str, Form(...)],
        price: Annotated[Decimal, Form(...)],
        stock: Annotated[int, Form(...)],
        category_id: Annotated[int, Form(...)],
    ):
        try:
            return cls(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category_id=category_id,
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())


class UpdateProductSchema(BaseModel):
    name: str | None = Field(description="Имя продукта", min_length=3)
    description: str | None = Field(description="Описание продукта", min_length=3)
    price: Decimal | None = Field(description="Цена продукта", ge=1)
    stock: int | None = Field(description="Количество продуктов", ge=0)
    category_id: int | None = Field(description="ID категории", ge=0)

    @classmethod
    def as_form(
        cls,
        name: Annotated[str | None, Form()] = None,
        description: Annotated[str | None, Form()] = None,
        price: Annotated[Decimal | None, Form()] = None,
        stock: Annotated[int | None, Form()] = None,
        category_id: Annotated[int | None, Form()] = None,
    ):
        try:
            return cls(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category_id=category_id,
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())

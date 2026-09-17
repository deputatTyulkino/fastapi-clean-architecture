from decimal import Decimal
from typing import Annotated

from fastapi import Form
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class CartItemSchema(BaseModel):
    id: int
    user_id: int
    product_id: int
    name: str
    price: Decimal
    quantity: int
    image_url: str
    model_config = ConfigDict(from_attributes=True)


class CreateCartItemSchema(BaseModel):
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(..., description="Количество", ge=1)

    @classmethod
    def as_form(
        cls,
        product_id: Annotated[int, Form(...)],
        quantity: Annotated[int, Form(...)],
    ):
        try:
            return cls(
                product_id=product_id,
                quantity=quantity,
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())

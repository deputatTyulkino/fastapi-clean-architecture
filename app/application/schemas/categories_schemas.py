from typing import Annotated

from fastapi import Form
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class CategorySchema(BaseModel):
    id: int
    name: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class CreateCategorySchema(BaseModel):
    name: str = Field(..., description="Название категории", min_length=3)

    @classmethod
    def as_form(cls, name: Annotated[str, Form(...)]):
        try:
            return cls(name=name)
        except ValidationError as e:
            raise RequestValidationError(e.errors())


class UpdateCategorySchema(BaseModel):
    name: str | None = Field(description="Название категории", min_length=3)

    @classmethod
    def as_form(cls, name: Annotated[str | None, Form()] = None):
        try:
            return cls(name=name)
        except ValidationError as e:
            raise RequestValidationError(e.errors())


class SuccessDeleteCategorySchema(BaseModel):
    detail: str

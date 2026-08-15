from datetime import datetime
from typing import Annotated

from fastapi import Form, Path
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.application.schemas.entities.users_schemas import UserSchema


class ReviewSchema(BaseModel):
    id: int
    user: UserSchema
    comment: str | None
    comment_date: datetime
    grade: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class CreateReviewSchema(BaseModel):
    product_id: int = Field(..., ge=0, description="ID товара")
    comment: str | None = Field(min_length=3, description="Текст отзыва")
    grade: int = Field(..., ge=1, le=5, description="Оценка товара")

    @classmethod
    def as_form(
        cls,
        product_id: Annotated[int, Path(...)],
        grade: Annotated[int, Form(...)],
        comment: Annotated[str | None, Form()] = None,
    ):
        try:
            return cls(product_id=product_id, grade=grade, comment=comment)
        except ValidationError as e:
            raise RequestValidationError(e.errors())


class UpdateReviewSchema(BaseModel):
    comment: str | None = Field(min_length=3, description="Текст отзыва")
    grade: int | None = Field(ge=1, le=5, description="Оценка товара")

    @classmethod
    def as_form(
        cls,
        grade: Annotated[int | None, Form()] = None,
        comment: Annotated[str | None, Form()] = None,
    ):
        try:
            return cls(grade=grade, comment=comment)
        except ValidationError as e:
            raise RequestValidationError(e.errors())

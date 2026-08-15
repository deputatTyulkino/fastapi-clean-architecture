from typing import Annotated

from fastapi import Path, Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError, model_validator


class QueryParamsProductsSchema(BaseModel):
    page: int = Field(default=1, ge=1, description="Номер страницы")
    limit: int = Field(
        default=6, ge=1, le=100, description="Количество элементов на странице"
    )
    search: str | None = Field(min_length=1, description="Поиск по названию товара")
    min_price: float | None = Field(ge=0, description="Минимальная цена товара")
    max_price: float | None = Field(ge=0, description="Максимальная цена товара")
    seller_id: int | None = Field(ge=0, description="ID продавца для фильтрации")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

    @model_validator(mode="after")
    def validate_price(self):
        if self.min_price and self.max_price and self.max_price < self.min_price:
            raise ValueError("Минимальная цена не может быть больше максимальной")
        return self

    @classmethod
    def as_form(
        cls,
        page: Annotated[int, Query(...)] = 1,
        limit: Annotated[int, Query(...)] = 6,
        search: Annotated[str | None, Query()] = None,
        min_price: Annotated[float | None, Query()] = None,
        max_price: Annotated[float | None, Query()] = None,
        seller_id: Annotated[int | None, Query()] = None,
    ):
        try:
            return cls(
                page=page,
                limit=limit,
                search=search,
                min_price=min_price,
                max_price=max_price,
                seller_id=seller_id,
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())

    def model_dump(self, **kwargs):
        return {
            **super().model_dump(**kwargs),
            "offset": self.offset,
        }


class ParamsReviewsSchema(BaseModel):
    product_id: int = Field(ge=0, description="ID товара для фильтрации")
    limit: int = Field(default=10, ge=0, description="Количество отзывов для вывода")
    page: int = Field(default=0, ge=0, description="Страница")
    grade: int | None = Field(default=None, ge=0, le=5, description="Оценка отзыва")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

    @classmethod
    def as_form(
        cls,
        product_id: Annotated[int, Path(...)],
        limit: Annotated[int, Query(...)] = 10,
        page: Annotated[int, Query(...)] = 0,
        grade: Annotated[int | None, Query()] = None,
    ):
        try:
            return cls(
                product_id=product_id,
                limit=limit,
                page=page,
                grade=grade,
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())

    def model_dump(self, **kwargs):
        return {
            **super().model_dump(**kwargs),
            "offset": self.offset,
        }

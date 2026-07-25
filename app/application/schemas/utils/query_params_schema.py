from typing import Annotated

from fastapi import Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError, model_validator


class QueryParamsSchema(BaseModel):
    page: int = Field(default=1, ge=1, description="Номер страницы")
    limit: int = Field(
        default=6, ge=1, le=100, description="Количество элементов на странице"
    )
    search: str | None = Field(min_length=1, description="Поиск по названию товара")
    category_id: int | None = Field(ge=1, description="ID категории для фильтрации")
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
        category_id: Annotated[int | None, Query()] = None,
        min_price: Annotated[float | None, Query()] = None,
        max_price: Annotated[float | None, Query()] = None,
        seller_id: Annotated[int | None, Query()] = None,
    ):
        try:
            return cls(
                page=page,
                limit=limit,
                search=search,
                category_id=category_id,
                min_price=min_price,
                max_price=max_price,
                seller_id=seller_id,
            )
        except ValidationError as e:
            raise RequestValidationError(e.errors())

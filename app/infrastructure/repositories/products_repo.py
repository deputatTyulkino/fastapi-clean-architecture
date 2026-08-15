from typing import Any

from sqlalchemy import ColumnElement, exists, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.domain.interfaces.repositories.i_product_repo import IProductRepo
from app.domain.models.products import (
    MainProductsDomain,
    ProductDomain,
)
from app.infrastructure.models.products import ProductORM


class ProductRepo(IProductRepo):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_orm_model(self, product: ProductDomain) -> ProductORM:
        return ProductORM(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            image_url=product.image_url,
            stock=product.stock,
            is_active=product.is_active,
            rating=product.rating,
            category_id=product.category_id,
            seller_id=product.seller_id,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    def _to_domain_model(self, product: ProductORM) -> ProductDomain:
        return ProductDomain(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            image_url=product.image_url,
            stock=product.stock,
            is_active=product.is_active,
            rating=product.rating,
            category_id=product.category_id,
            seller_id=product.seller_id,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    def _to_domain_catalog_model(self, product: ProductORM) -> MainProductsDomain:
        return MainProductsDomain(
            id=product.id,
            name=product.name,
            price=product.price,
            image_url=product.image_url,
            rating=product.rating,
        )

    async def get_all(
        self, params: dict[str, Any]
    ) -> tuple[list[MainProductsDomain], int, int, int]:
        filters: list[ColumnElement[bool]] = [ProductORM.is_active.is_(True)]
        search = params.get("search")
        seller_id = params.get("seller_id")
        min_price = params.get("min_price")
        max_price = params.get("max_price")
        if seller_id is not None:
            filters.append(ProductORM.seller_id == seller_id)
        if min_price is not None:
            filters.append(ProductORM.price >= min_price)
        if max_price is not None:
            filters.append(ProductORM.price <= max_price)

        total_stmt = select(func.count()).select_from(ProductORM).filter(*filters)
        rank_col = None

        if search is not None:
            search_value = search.strip()
            if search_value:
                ts_query_ru = func.websearch_to_tsquery("russian", search_value)
                ts_query = ProductORM.tsv.match(ts_query_ru)
                filters.append(ts_query)
                rank_col = func.ts_rank_cd(ProductORM.tsv, ts_query_ru).label("rank")
                total_stmt = (
                    select(func.count()).select_from(ProductORM).filter(*filters)
                )

        total = await self.db.scalar(total_stmt) or 0
        if rank_col is not None:
            products_stmt = (
                select(ProductORM, rank_col)
                .options(
                    load_only(
                        ProductORM.id,
                        ProductORM.name,
                        ProductORM.price,
                        ProductORM.image_url,
                        ProductORM.rating,
                    )
                )
                .filter(*filters)
                .order_by(rank_col.desc(), ProductORM.id)
                .offset(params["offset"])
                .limit(params["limit"])
            )
            products_stmt_res = (await self.db.scalars(products_stmt)).all()
            products = [
                self._to_domain_catalog_model(pr[0]) for pr in products_stmt_res
            ]
        else:
            products_stmt = (
                select(ProductORM)
                .options(
                    load_only(
                        ProductORM.id,
                        ProductORM.name,
                        ProductORM.price,
                        ProductORM.image_url,
                        ProductORM.rating,
                    )
                )
                .filter(*filters)
                .order_by(ProductORM.id)
                .offset(params["offset"])
                .limit(params["limit"])
            )
            products_stmt_res = (await self.db.scalars(products_stmt)).all()
            products = [self._to_domain_catalog_model(pr) for pr in products_stmt_res]
        return products, total, params["page"], params["limit"]

    async def get_by_category(self, id: int) -> list[MainProductsDomain]:
        stmt = (
            select(ProductORM)
            .filter(ProductORM.category_id == id, ProductORM.is_active)
            .options(
                load_only(
                    ProductORM.id,
                    ProductORM.name,
                    ProductORM.price,
                    ProductORM.image_url,
                    ProductORM.rating,
                )
            )
        )
        products = (await self.db.scalars(stmt)).all()
        return [self._to_domain_catalog_model(product) for product in products]

    async def get_by_seller(self, id: int) -> list[MainProductsDomain]:
        stmt = (
            select(ProductORM)
            .filter(ProductORM.seller_id == id, ProductORM.is_active)
            .options(
                load_only(
                    ProductORM.id,
                    ProductORM.name,
                    ProductORM.price,
                    ProductORM.image_url,
                    ProductORM.rating,
                )
            )
        )
        products = (await self.db.scalars(stmt)).all()
        return [self._to_domain_catalog_model(product) for product in products]

    async def get_by_id(self, id: int) -> ProductDomain | None:
        stmt = select(ProductORM).filter(ProductORM.id == id, ProductORM.is_active)
        product = (await self.db.execute(stmt)).scalar_one_or_none()
        if product is None:
            return None
        return self._to_domain_model(product)

    async def exists_by_id(self, id: int) -> bool:
        stmt = select(exists().where(ProductORM.id == id, ProductORM.is_active))
        return bool(await self.db.scalar(stmt))

    async def exists_by_name(self, name: str) -> bool:
        stmt = select(exists().where(ProductORM.name == name, ProductORM.is_active))
        return bool(await self.db.scalar(stmt))

    async def create(self, product_data: ProductDomain) -> ProductDomain:
        new_product = self._to_orm_model(product_data)
        self.db.add(new_product)
        await self.db.flush()
        return self._to_domain_model(new_product)

    async def update(
        self, id: int, product_data: ProductDomain
    ) -> ProductDomain | None:
        stmt = (
            update(ProductORM)
            .filter(ProductORM.id == id, ProductORM.is_active)
            .values(**product_data.filtered_none_fields())
            .returning(ProductORM)
        )
        product = (await self.db.execute(stmt)).scalar_one_or_none()
        if product is None:
            return None
        return self._to_domain_model(product)

    async def delete(self, id: int) -> int | None:
        stmt = (
            update(ProductORM)
            .filter(ProductORM.id == id, ProductORM.is_active)
            .values(is_active=False)
            .returning(ProductORM.id)
        )
        product_id = (await self.db.execute(stmt)).scalar_one_or_none()
        return product_id

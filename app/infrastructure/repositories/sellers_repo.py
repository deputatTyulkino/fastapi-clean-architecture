from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload

from app.domain.interfaces.repositories.i_seller_repo import ISellerRepo
from app.domain.models.sellers import SellerDomain
from app.infrastructure.models.products import ProductORM
from app.infrastructure.models.sellers import SellerORM


class SellerRepo(ISellerRepo):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_orm_model(self, seller: SellerDomain) -> SellerORM:
        return SellerORM(
            id=seller.id,
            user_id=seller.user_id,
            description=seller.description,
            store_name=seller.store_name,
            logo_url=seller.logo_url,
            banner_url=seller.banner_url,
            legal_name=seller.legal_name,
            tax_id=seller.tax_id,
            phone=seller.phone,
            status=seller.status,
            rating=seller.rating,
            reviews_count=seller.reviews_count,
            created_at=seller.created_at,
            updated_at=seller.updated_at,
            is_active=seller.is_active,
        )

    def _to_domain_model(self, seller: SellerORM) -> SellerDomain:
        return SellerDomain(
            id=seller.id,
            user_id=seller.user_id,
            description=seller.description,
            store_name=seller.store_name,
            logo_url=seller.logo_url,
            banner_url=seller.banner_url,
            legal_name=seller.legal_name,
            tax_id=seller.tax_id,
            phone=seller.phone,
            status=seller.status,
            rating=seller.rating,
            reviews_count=seller.reviews_count,
            created_at=seller.created_at,
            updated_at=seller.updated_at,
            is_active=seller.is_active,
        )

    async def get_by_id(self, id: int) -> SellerDomain | None:
        query = select(SellerORM).filter_by(id=id)
        seller = (await self.db.execute(query)).scalar_one_or_none()
        if seller is None:
            return None
        return self._to_domain_model(seller)

    async def exists_by_id(self, id: int) -> bool:
        stmt = select(exists().where(SellerORM.id == id))
        return bool(await self.db.scalar(stmt))

    async def get_by_product_id(self, product_id: int) -> SellerDomain | None:
        s = aliased(SellerORM)
        p = aliased(ProductORM)
        query = (
            select(s)
            .select_from(p)
            .filter(p.id == product_id)
            .options(joinedload(p.seller))
        )
        seller = (await self.db.execute(query)).scalar_one_or_none()
        if seller is None:
            return None
        return self._to_domain_model(seller)

    async def create(self, seller_data: SellerDomain) -> SellerDomain:
        seller = self._to_orm_model(seller_data)
        self.db.add(seller)
        await self.db.flush()
        return self._to_domain_model(seller)

    async def update(self, id: int, seller_data: SellerDomain) -> SellerDomain | None:
        stmt = (
            update(SellerORM)
            .filter(SellerORM.id == id)
            .values(**seller_data.filtered_none_fields())
            .returning(SellerORM)
        )
        seller = (await self.db.execute(stmt)).scalar_one_or_none()
        if seller is None:
            return None
        return self._to_domain_model(seller)

    async def delete(self, id: int) -> int | None:
        stmt = (
            update(SellerORM)
            .filter(SellerORM.id == id)
            .values(is_active=False)
            .returning(SellerORM.id)
        )
        seller_id = (await self.db.execute(stmt)).scalar_one_or_none()
        return seller_id

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.repositories.i_review_repo import IReviewsRepo
from app.domain.models.reviews import ReviewDomain
from app.infrastructure.models.reviews import ReviewORM


class ReviewRepo(IReviewsRepo):
    def __init__(self, db: AsyncSession, logger: ILogger):
        self.db = db
        self.logger = logger.bind(repository="ReviewRepo")

    def _to_orm_model(self, review: ReviewDomain) -> ReviewORM:
        return ReviewORM(
            id=review.id,
            user_id=review.user_id,
            product_id=review.product_id,
            comment=review.comment,
            comment_date=review.comment_date,
            grade=review.grade,
            is_active=review.is_active,
        )

    def _to_domain_model(self, review: ReviewORM) -> ReviewDomain:
        return ReviewDomain(
            id=review.id,
            user_id=review.user_id,
            product_id=review.product_id,
            comment=review.comment,
            comment_date=review.comment_date,
            grade=review.grade,
            is_active=review.is_active,
        )

    async def get_all(self, params: dict[str, int | None]) -> list[ReviewDomain]:
        offset = params.get("offset", 0)
        limit = params.get("limit", 10)
        product_id = params.get("product_id")
        query = (
            select(ReviewORM)
            .filter(ReviewORM.product_id == product_id, ReviewORM.is_active)
            .offset(offset)
            .limit(limit)
        )
        reviews = (await self.db.scalars(query)).all()
        self.logger.debug("reviews_fetched", product_id=product_id, count=len(reviews))
        return [self._to_domain_model(review) for review in reviews]

    async def get_by_id(self, review_id: int) -> ReviewDomain | None:
        query = select(ReviewORM).filter(ReviewORM.id == review_id, ReviewORM.is_active)
        review = (await self.db.execute(query)).scalar_one_or_none()
        if review is None:
            self.logger.debug("review_not_found", review_id=review_id)
            return None
        return self._to_domain_model(review)

    async def get_top_reviews(self, product_id: int) -> list[ReviewDomain]:
        query = (
            select(ReviewORM)
            .filter(ReviewORM.product_id == product_id, ReviewORM.is_active)
            .order_by(ReviewORM.grade.desc(), ReviewORM.id)
            .limit(3)
        )
        reviews = (await self.db.scalars(query)).all()
        self.logger.debug(
            "top_reviews_fetched", product_id=product_id, count=len(reviews)
        )
        return [self._to_domain_model(review) for review in reviews]

    async def create(self, review_data: ReviewDomain) -> ReviewDomain:
        review = self._to_orm_model(review_data)
        self.db.add(review)
        await self.db.flush()
        self.logger.info(
            "review_created",
            review_id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            grade=review.grade,
        )
        return self._to_domain_model(review)

    async def update(
        self, review_id: int, review_data: ReviewDomain
    ) -> ReviewDomain | None:
        stmt = (
            update(ReviewORM)
            .filter(ReviewORM.id == review_id)
            .values(**review_data.filtered_none_fields())
            .returning(ReviewORM)
        )
        review = (await self.db.execute(stmt)).scalar_one_or_none()
        if review is None:
            self.logger.warning("review_update_not_found", review_id=review_id)
            return None
        self.logger.info("review_updated", review_id=review_id)
        return self._to_domain_model(review)

    async def delete(self, review_id: int) -> int | None:
        stmt = (
            update(ReviewORM)
            .filter(ReviewORM.id == review_id)
            .values(is_active=False)
            .returning(ReviewORM.id)
        )
        rev_id = (await self.db.execute(stmt)).scalar_one_or_none()
        if rev_id is None:
            self.logger.warning("review_delete_not_found", review_id=review_id)
            return None
        self.logger.info("review_deleted", review_id=rev_id)
        return rev_id

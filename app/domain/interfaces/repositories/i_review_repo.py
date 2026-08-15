from abc import ABC, abstractmethod

from app.domain.models.reviews import ReviewDomain


class IReviewsRepo(ABC):
    @abstractmethod
    async def get_all(self, params: dict[str, int | None]) -> list[ReviewDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def get_top_reviews(self, product_id: int) -> list[ReviewDomain]:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_id(self, review_id: int) -> ReviewDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def create(self, review_data: ReviewDomain) -> ReviewDomain:
        raise NotImplementedError()

    @abstractmethod
    async def update(
        self, review_id: int, review_data: ReviewDomain
    ) -> ReviewDomain | None:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, review_id: int) -> int | None:
        raise NotImplementedError()

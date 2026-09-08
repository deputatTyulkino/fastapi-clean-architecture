import asyncio

from app.application.schemas.entities.reviews_schemas import (
    CreateReviewSchema,
    ReviewSchema,
    UpdateReviewSchema,
)
from app.application.schemas.entities.users_schemas import UserSchema
from app.application.schemas.utils.query_params_schema import ParamsReviewsSchema
from app.application.schemas.utils.success_delete_schema import SuccessDeleteSchema
from app.domain.interfaces.redis.i_cache_client import ICacheClient
from app.domain.interfaces.redis.i_state_client import IStateClient
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.models.reviews import ReviewDomain
from app.domain.models.users import UserDomain
from app.infrastructure.redis.decorators import redis_cache


class ReviewServices:
    def __init__(
        self, uow: IUnitOfWork, cache_client: ICacheClient, state_client: IStateClient
    ):
        self.uow = uow
        self.cache_client = cache_client
        self.state_client = state_client

    @redis_cache(
        lambda product_id: f"products:{product_id}:reviews", 500, list[ReviewSchema]
    )
    async def get_all_reviews(
        self, query_params: ParamsReviewsSchema
    ) -> list[ReviewSchema]:
        users = []
        users_tasks: list[asyncio.Task[UserDomain | None]] = []
        async with self.uow as uow:
            exists_product = await uow.products.exists_by_id(query_params.product_id)
            if not exists_product:
                raise ValueError(
                    f"Продукта c ID {query_params.product_id} не существует"
                )
            reviews = await uow.reviews.get_all(query_params.model_dump())
            async with asyncio.TaskGroup() as tg:
                for review in reviews:
                    users_tasks.append(
                        tg.create_task(uow.users.get_by_id(review.user_id))
                    )
        for user_task in users_tasks:
            user = user_task.result()
            if user is None:
                raise ValueError("Пользователь не найден")
            users.append(user)
        return [
            ReviewSchema(**review.as_dict(), user=UserSchema.model_validate(users[ind]))
            for ind, review in enumerate(reviews)
        ]

    @redis_cache(
        lambda product_id: f"products:{product_id}:reviews:top", 500, list[ReviewSchema]
    )
    async def get_top_reviews(self, product_id: int) -> list[ReviewSchema]:
        users_top_reviews = []
        users_top_reviews_tasks: list[asyncio.Task[UserDomain | None]] = []
        async with self.uow as uow:
            exists_product = await uow.products.exists_by_id(product_id)
            if not exists_product:
                raise ValueError(f"Продукта с ID {product_id} не существует")
            reviews = await uow.reviews.get_top_reviews(product_id)
            async with asyncio.TaskGroup() as tg:
                for review in reviews:
                    users_top_reviews_tasks.append(
                        tg.create_task(uow.users.get_by_id(review.user_id))
                    )
        for user_task in users_top_reviews_tasks:
            user = user_task.result()
            if user is None:
                raise ValueError("Пользователь не найден")
            users_top_reviews.append(user)
        return [
            ReviewSchema(
                **review.as_dict(),
                user=UserSchema.model_validate(users_top_reviews[ind]),
            )
            for ind, review in enumerate(reviews)
        ]

    async def create_review(
        self, review_data: CreateReviewSchema, user_id: int
    ) -> ReviewSchema:
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise ValueError(f"Пользователя с ID {user_id} не существует")
            exists_product = await uow.products.exists_by_id(review_data.product_id)
            if not exists_product:
                raise ValueError(
                    f"Продукта с ID {review_data.product_id} не существует"
                )
            review = await uow.reviews.create(
                ReviewDomain(user_id=user_id, **review_data.model_dump())
            )
            await uow.commit()
        await self.state_client.sadd(
            "dirty_products_ids", f"products:{review.product_id}"
        )
        await self.cache_client.delete(
            f"products:{review.product_id}:reviews",
            f"products:{review.product_id}:reviews:top",
        )
        return ReviewSchema(**review.as_dict(), user=UserSchema.model_validate(user))

    async def update_review(
        self, id: int, review_data: UpdateReviewSchema, user_id: int
    ) -> ReviewSchema:
        async with self.uow as uow:
            review = await uow.reviews.get_by_id(id)
            if review is None:
                raise ValueError(f"Отзыва с ID {id} не существует")
            if review.user_id != user_id:
                raise ValueError("У вас нет прав на изменение этого отзыва")
            review_coroutine = uow.reviews.update(
                id, ReviewDomain(**review_data.model_dump())
            )
            user_coroutine = uow.users.get_by_id(review.user_id)
            review, user = await asyncio.gather(review_coroutine, user_coroutine)
            if review is None:
                raise ValueError(f"Не удалось обновить отзыв с ID {id}")
            await uow.commit()
        await self.cache_client.delete(
            f"products:{review.product_id}:reviews",
            f"products:{review.product_id}:reviews:top",
        )
        return ReviewSchema(**review.as_dict(), user=UserSchema.model_validate(user))

    async def delete_review(
        self, id: int, user_id: int, is_admin: bool | None
    ) -> SuccessDeleteSchema:
        async with self.uow as uow:
            review = await uow.reviews.get_by_id(id)
            if review is None:
                raise ValueError(f"Отзыва с ID {id} не существует")
            if review.user_id != user_id and not is_admin:
                raise ValueError("У вас нет прав на удаление этого отзыва")
            review_id = await uow.reviews.delete(id)
            await uow.commit()
        await self.cache_client.delete(
            f"products:{review.product_id}:reviews",
            f"products:{review.product_id}:reviews:top",
        )
        return SuccessDeleteSchema(detail=f"Отзыв с ID {review_id} успешно удалён")

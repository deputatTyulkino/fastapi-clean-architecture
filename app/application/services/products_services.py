from asyncio import Task, TaskGroup
from decimal import Decimal

from app.application.schemas.entities.products_schemas import (
    CreateProductSchema,
    MainInfoProductSchema,
    ProductSchema,
    UpdateProductSchema,
)
from app.application.schemas.utils.query_params_schema import QueryParamsProductsSchema
from app.application.schemas.utils.success_delete_schema import SuccessDeleteSchema
from app.application.schemas.utils.success_response_schema import (
    SuccessPaginatedResponseSchema,
)
from app.domain.interfaces.redis.i_cache_client import ICacheClient
from app.domain.interfaces.redis.i_serializer_services import ISerializerServices
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.interfaces.utils.i_image_storage import IImageServices
from app.domain.models.files import FileDomain
from app.domain.models.products import ProductDomain
from app.infrastructure.redis.decorators import redis_cache


class ProductServices:
    def __init__(
        self,
        uow: IUnitOfWork,
        image_services: IImageServices,
        serializer_services: ISerializerServices,
        cache_client: ICacheClient,
    ):
        self.uow = uow
        self.image_services = image_services
        self.serializer_services = serializer_services
        self.cache_client = cache_client

    @redis_cache(
        lambda _: "all_products",
        1000,
        SuccessPaginatedResponseSchema[MainInfoProductSchema],
    )
    async def get_all_products(
        self, query_params: QueryParamsProductsSchema
    ) -> SuccessPaginatedResponseSchema[MainInfoProductSchema]:
        filters = query_params.model_dump(exclude_unset=True)
        seller_id = filters.get("seller_id")
        async with self.uow as uow:
            if seller_id is not None:
                exists_seller = await uow.sellers.exists_by_id(seller_id)
                if not exists_seller:
                    raise ValueError(f"Продавца с ID {seller_id} не существует")
            products, total, page, limit = await uow.products.get_all(filters)
            products_rating: list[tuple[int, Task[Decimal] | Decimal]] = []
            async with TaskGroup() as tg:
                for product in products:
                    cache_rating = await self.cache_client.get(
                        f"products:{product.id}:rating"
                    )
                    if cache_rating is not None:
                        products_rating.append(
                            (
                                product.id,
                                self.serializer_services.deserializer(
                                    cache_rating, Decimal
                                ),
                            )
                        )
                    else:
                        products_rating.append(
                            (
                                product.id,
                                tg.create_task(
                                    uow.products.get_rating_by_id(product.id)
                                ),
                            )
                        )
            ratings: dict[int, Decimal] = {}
            for ratings_info in products_rating:
                product_id = ratings_info[0]
                info = ratings_info[1]
                if isinstance(info, Task):
                    rating = info.result()
                    serilized_rating = self.serializer_services.serializer(
                        rating, Decimal
                    )
                    if serilized_rating is None:
                        raise RuntimeError("Ошибка сериализации")
                    await self.cache_client.set(
                        f"products:{product_id}:rating", serilized_rating, 100
                    )
                    ratings[product_id] = rating
                else:
                    ratings[product_id] = info
        return SuccessPaginatedResponseSchema[MainInfoProductSchema](
            items=[
                MainInfoProductSchema(**product.as_dict(), rating=ratings[product.id])
                for product in products
            ],
            total=total,
            page=page,
            limit=limit,
        )

    @redis_cache(lambda id: f"products:{id}", 100, ProductSchema)
    async def get_product_by_id(self, id: int) -> ProductSchema:
        async with self.uow as uow:
            product = await uow.products.get_by_id(id)
            if product is None:
                raise ValueError(f"Продукта с ID {id} не существует")
            cache_rating = await self.cache_client.get(f"products:{id}:rating")
            if cache_rating is None:
                products_rating = await uow.products.get_rating_by_id(id)
                serialized_rating = self.serializer_services.serializer(
                    products_rating, Decimal
                )
                if serialized_rating is None:
                    raise RuntimeError("Ошибка сериализации")
                await self.cache_client.set(
                    f"products:{id}:rating", serialized_rating, 100
                )
            else:
                products_rating = self.serializer_services.deserializer(
                    cache_rating, Decimal
                )
        return ProductSchema(**product.as_dict(), rating=products_rating)

    @redis_cache(
        lambda cat_id: f"products:category:{cat_id}", 100, list[MainInfoProductSchema]
    )
    async def get_products_by_category(
        self, category_id: int
    ) -> list[MainInfoProductSchema]:
        async with self.uow as uow:
            exists_category = await uow.categories.exists_by_id(category_id)
            if not exists_category:
                raise ValueError(f"Категории с ID {category_id} не существует")
            products = await uow.products.get_by_category(category_id)
            products_rating: list[tuple[int, Task[Decimal] | Decimal]] = []
            async with TaskGroup() as tg:
                for product in products:
                    cache_rating = await self.cache_client.get(
                        f"products:{product.id}:rating"
                    )
                    if cache_rating is not None:
                        products_rating.append(
                            (
                                product.id,
                                self.serializer_services.deserializer(
                                    cache_rating, Decimal
                                ),
                            )
                        )
                    else:
                        products_rating.append(
                            (
                                product.id,
                                tg.create_task(
                                    uow.products.get_rating_by_id(product.id)
                                ),
                            )
                        )
            ratings: dict[int, Decimal] = {}
            for ratings_info in products_rating:
                product_id = ratings_info[0]
                info = ratings_info[1]
                if isinstance(info, Task):
                    rating = info.result()
                    serilized_rating = self.serializer_services.serializer(
                        rating, Decimal
                    )
                    if serilized_rating is None:
                        raise RuntimeError("Ошибка сериализации")
                    await self.cache_client.set(
                        f"products:{product_id}:rating", serilized_rating, 100
                    )
                    ratings[product_id] = rating
                else:
                    ratings[product_id] = info
        return [
            MainInfoProductSchema(**product.as_dict(), rating=ratings[product.id])
            for product in products
        ]

    async def create_product(
        self, product_data: CreateProductSchema, image: FileDomain, seller_id: int
    ) -> ProductSchema:
        async with self.uow as uow:
            category = await uow.categories.get_by_id(product_data.category_id)
            if category is None:
                raise ValueError(
                    f"Категории с ID {product_data.category_id} не существует"
                )
            exists_product = await uow.products.exists_by_name(product_data.name)
            if exists_product:
                raise ValueError(f"Продукт с именем {product_data.name} уже существует")
            new_image = await self.image_services.save_image(image, "products")
            new_product = await uow.products.create(
                ProductDomain(
                    **product_data.model_dump(),
                    image_url=new_image,
                    seller_id=seller_id,
                )
            )
            await uow.commit()
        await self.cache_client.delete(
            "all_products", f"products:category:{product_data.category_id}"
        )
        return ProductSchema.model_validate(new_product)

    async def update_product(
        self,
        product_id: int,
        product_data: UpdateProductSchema,
        image: FileDomain | None,
        user_id: int,
    ) -> ProductSchema:
        async with self.uow as uow:
            if product_data.name:
                exists_product = await uow.products.exists_by_name(product_data.name)
                if exists_product:
                    raise ValueError(
                        f"Продукт с именем {product_data.name} уже существует"
                    )
            if product_data.category_id:
                exists_category = await uow.categories.exists_by_id(
                    product_data.category_id
                )
                if not exists_category:
                    raise ValueError(
                        f"Категории с ID {product_data.category_id} не существует"
                    )
            product = await uow.products.get_by_id(product_id)
            if product is None:
                raise ValueError(f"Товара с таким ID {product_id} не существует")
            if product.seller_id != user_id:
                raise ValueError("У вас нет прав изменять этот продукт")
            if image:
                if product.image_url:
                    await self.image_services.remove_image(product.image_url)
                new_image = await self.image_services.save_image(image, "products")
                updated_product = await uow.products.update(
                    product_id,
                    ProductDomain(**product_data.model_dump(), image_url=new_image),
                )
            else:
                updated_product = await uow.products.update(
                    product_id, ProductDomain(**product_data.model_dump())
                )
            await uow.commit()
        await self.cache_client.delete(
            "all_products",
            f"products:category:{product_data.category_id}",
            f"products:{product_id}",
        )
        return ProductSchema.model_validate(updated_product)

    async def delete_product(
        self, id: int, user_id: int, is_admin: bool | None
    ) -> SuccessDeleteSchema:
        async with self.uow as uow:
            product = await uow.products.get_by_id(id)
            if product is None:
                raise ValueError(f"Товара с таким ID {id} не существует")
            if product.seller_id != user_id and not is_admin:
                raise ValueError("У вас нет прав на удаление этого товара")
            if product.image_url:
                await self.image_services.remove_image(product.image_url)
            product_id = await uow.products.delete(id)
            await uow.commit()
        await self.cache_client.delete(
            "all_products",
            f"products:category:{product.category_id}",
            f"products:{product_id}",
        )
        return SuccessDeleteSchema(detail=f"Товар с ID {product_id} успешно удалён")

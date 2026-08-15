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
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.interfaces.utils.i_image_storage import IImageStorage
from app.domain.models.files import FileDomain
from app.domain.models.products import ProductDomain


class ProductServices:
    def __init__(self, uow: IUnitOfWork, image_storage: IImageStorage):
        self.uow = uow
        self.image_storage = image_storage

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
        return SuccessPaginatedResponseSchema[MainInfoProductSchema](
            items=[
                MainInfoProductSchema.model_validate(product) for product in products
            ],
            total=total,
            page=page,
            limit=limit,
        )

    async def get_product_by_id(self, id: int) -> ProductSchema:
        async with self.uow as uow:
            product = await uow.products.get_by_id(id)
            if product is None:
                raise ValueError(f"Товара с ID {id} не существует")
        return ProductSchema.model_validate(product)

    async def get_products_by_category(
        self, category_id: int
    ) -> list[MainInfoProductSchema]:
        async with self.uow as uow:
            exists_category = await uow.categories.exists_by_id(category_id)
            if not exists_category:
                raise ValueError(f"Категории с ID {category_id} не существует")
            products = await uow.products.get_by_category(category_id)
        return [MainInfoProductSchema.model_validate(product) for product in products]

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
            new_image = await self.image_storage.save_image(image, "products")
            new_product = await uow.products.create(
                ProductDomain(
                    **product_data.model_dump(),
                    image_url=new_image,
                    seller_id=seller_id,
                )
            )
            await uow.commit()
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
                    await self.image_storage.remove_image(product.image_url)
                new_image = await self.image_storage.save_image(image, "products")
                updated_product = await uow.products.update(
                    product_id,
                    ProductDomain(**product_data.model_dump(), image_url=new_image),
                )
            else:
                updated_product = await uow.products.update(
                    product_id, ProductDomain(**product_data.model_dump())
                )
            await uow.commit()
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
                await self.image_storage.remove_image(product.image_url)
            product_id = await uow.products.delete(id)
            await uow.commit()
        return SuccessDeleteSchema(detail=f"Товар с ID {product_id} успешно удалён")

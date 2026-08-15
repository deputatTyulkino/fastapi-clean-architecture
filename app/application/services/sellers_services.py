from app.application.schemas.entities.sellers_schemas import (
    CreateSellerProfileSchema,
    SellerProfileSchema,
    UpdateSellerProfileSchema,
)
from app.application.schemas.entities.users_schemas import UserSchema
from app.application.schemas.utils.success_delete_schema import SuccessDeleteSchema
from app.domain.interfaces.uow.i_unit_of_work import IUnitOfWork
from app.domain.interfaces.utils.i_image_storage import IImageStorage
from app.domain.models.files import FileDomain
from app.domain.models.sellers import SellerDomain


class SellerServices:
    def __init__(self, uow: IUnitOfWork, image_storage: IImageStorage):
        self.uow = uow
        self.image_storage = image_storage

    async def get_seller_by_id(self, id: int) -> SellerProfileSchema:
        async with self.uow as uow:
            seller = await uow.sellers.get_by_id(id)
            if seller is None:
                raise ValueError(f"Аккаунта продавца с ID {id} не существует")
            user = await uow.users.get_by_id(seller.user_id)
            if user is None:
                raise ValueError(f"Пользователь с ID {seller.user_id} не существует")
        return SellerProfileSchema(
            user=UserSchema.model_validate(user),
            **seller.as_dict(),
        )

    async def get_seller_by_product(self, product_id: int) -> SellerProfileSchema:
        async with self.uow as uow:
            exists_product = await uow.products.exists_by_id(product_id)
            if not exists_product:
                raise ValueError(f"Продукта с ID {product_id} не существует")
            seller = await uow.sellers.get_by_product_id(product_id)
            if seller is None:
                raise ValueError("Продавец не найден")
            user = await uow.users.get_by_id(seller.user_id)
        return SellerProfileSchema(
            **seller.as_dict(), user=UserSchema.model_validate(user)
        )

    async def create_seller(
        self,
        logo: FileDomain | None,
        banner: FileDomain | None,
        seller_data: CreateSellerProfileSchema,
    ) -> SellerProfileSchema:
        async with self.uow as uow:
            exists_user = await uow.users.exists_by_id(seller_data.user_id)
            if not exists_user:
                raise ValueError(
                    f"Пользователя с ID {seller_data.user_id} не существует"
                )
            new_logo = (
                await self.image_storage.save_image(logo, "logos") if logo else None
            )
            new_banner = (
                await self.image_storage.save_image(banner, "banners")
                if banner
                else None
            )
            seller = await uow.sellers.create(
                SellerDomain(
                    **seller_data.model_dump(), logo_url=new_logo, banner_url=new_banner
                )
            )
            await uow.commit()
            user = await uow.users.get_by_id(seller.user_id)
            if user is None:
                raise ValueError(f"Пользователь с ID {seller.user_id} не существует")
        return SellerProfileSchema(
            user=UserSchema.model_validate(user),
            **seller.as_dict(),
        )

    async def update_seller(
        self,
        id: int,
        logo: FileDomain | None,
        banner: FileDomain | None,
        seller_data: UpdateSellerProfileSchema,
    ) -> SellerProfileSchema:
        async with self.uow as uow:
            seller = await uow.sellers.get_by_id(id)
            if seller is None:
                raise ValueError(f"Нет информации по профилю с ID {id}")
            if seller.logo_url and logo:
                await self.image_storage.remove_image(seller.logo_url)
            new_logo = (
                await self.image_storage.save_image(logo, "logos") if logo else None
            )
            if seller.banner_url and banner:
                await self.image_storage.remove_image(seller.banner_url)
            new_banner = (
                await self.image_storage.save_image(banner, "banners")
                if banner
                else None
            )
            new_seller = await uow.sellers.update(
                id,
                SellerDomain(
                    **seller_data.model_dump(), logo_url=new_logo, banner_url=new_banner
                ),
            )
            if new_seller is None:
                await uow.rollback()
                raise ValueError("Не удалось обновить профиль")
            await uow.commit()
            user = await uow.users.get_by_id(seller.user_id)
            if user is None:
                raise ValueError(
                    f"Пользователь с ID {new_seller.user_id} не существует"
                )
        return SellerProfileSchema(
            user=UserSchema.model_validate(user),
            **new_seller.as_dict(),
        )

    async def delete_seller(self, id: int) -> SuccessDeleteSchema:
        async with self.uow as uow:
            seller = await uow.sellers.get_by_id(id)
            if seller is None:
                raise ValueError(f"Нет информации по профилю с ID {id}")
            if seller.logo_url:
                await self.image_storage.remove_image(seller.logo_url)
            if seller.banner_url:
                await self.image_storage.remove_image(seller.banner_url)
            seller_id = await uow.sellers.delete(id)
            if seller_id is None:
                await uow.rollback()
                raise ValueError(f"Не удалось удалить профиль с ID {id}")
            await uow.commit()
        return SuccessDeleteSchema(
            detail=f"Информация об аккаунте продавца с ID {seller_id} успешно удалена"
        )

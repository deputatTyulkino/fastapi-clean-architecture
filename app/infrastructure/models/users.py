from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.users import SellerStatus, UserRole
from app.infrastructure.database.connect import Base

if TYPE_CHECKING:
    from .cart_items import CartItemORM
    from .orders import OrderORM
    from .products import ProductORM
    from .reviews import ReviewORM


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool]
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="role", create_type=True)
    )

    products: Mapped[list["ProductORM"]] = relationship(back_populates="seller")
    reviews: Mapped[list["ReviewORM"]] = relationship(back_populates="user")
    cart_items: Mapped[list["CartItemORM"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    orders: Mapped[list["OrderORM"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    seller: Mapped["SellerORM"] = relationship(back_populates="user")


class SellerORM(Base):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    store_name: Mapped[str]
    logo_url: Mapped[str | None]
    banner_url: Mapped[str | None]
    legal_name: Mapped[str | None]
    tax_id: Mapped[str | None]
    phone: Mapped[str | None]
    status: Mapped[SellerStatus] = mapped_column(
        Enum(SellerStatus, name="seller_status", create_type=True)
    )
    rejection_reason: Mapped[str | None]
    rating: Mapped[Decimal]
    reviews_count: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["UserORM"] = relationship(back_populates="seller")

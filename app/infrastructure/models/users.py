from typing import TYPE_CHECKING

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.users import UserRole
from app.infrastructure.database.connect import Base

if TYPE_CHECKING:
    from .cart_items import CartItemORM
    from .orders import OrderORM
    from .reviews import ReviewORM
    from .sellers import SellerORM


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool]
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="role", create_type=True)
    )

    reviews: Mapped[list["ReviewORM"]] = relationship(back_populates="user")
    cart_items: Mapped[list["CartItemORM"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    orders: Mapped[list["OrderORM"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    seller: Mapped["SellerORM"] = relationship(back_populates="user")

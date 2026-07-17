from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.models.users import UserRole

if TYPE_CHECKING:
    from .cart_items import CartItem
    from .orders import Order
    from .products import ProductORM
    from .reviews import ReviewORM


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool]
    role: Mapped[UserRole]

    products: Mapped[list["ProductORM"]] = relationship(back_populates="seller")
    reviews: Mapped[list["ReviewORM"]] = relationship(back_populates="user")
    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

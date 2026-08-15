from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.sellers import SellerStatus
from app.infrastructure.database.connect import Base

if TYPE_CHECKING:
    from .products import ProductORM
    from .users import UserORM


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
    rating: Mapped[Decimal] = mapped_column(Numeric(2, 1))
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
    is_active: Mapped[bool]

    user: Mapped["UserORM"] = relationship(back_populates="seller")
    products: Mapped[list["ProductORM"]] = relationship(back_populates="seller")

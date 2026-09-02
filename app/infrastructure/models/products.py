from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connect import Base

if TYPE_CHECKING:
    from .cart_items import CartItemORM
    from .categories import CategoryORM
    from .orders import OrderItemORM
    from .reviews import ReviewORM
    from .users import SellerORM


class ProductORM(Base):
    __tablename__ = "products"
    __table_args__ = (Index("idx_products_tsv_gin", "tsv", postgresql_using="gin"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200))
    stock: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool]
    sum_grade: Mapped[int]
    reviews_count: Mapped[int]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tsv: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed(
            """
            setweight(to_tsvector('russian', coalesce(name, '')), 'A')
            ||
            setweight(to_tsvector('russian', coalesce(description, '')), 'B')
            """,
            persisted=True,
        ),
        nullable=False,
    )

    category: Mapped["CategoryORM"] = relationship(back_populates="products")
    seller: Mapped["SellerORM"] = relationship(back_populates="products")
    reviews: Mapped[list["ReviewORM"]] = relationship(back_populates="product")
    cart_items: Mapped[list["CartItemORM"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    order_items: Mapped[list["OrderItemORM"]] = relationship(back_populates="product")

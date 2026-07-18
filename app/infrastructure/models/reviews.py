from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from .products import ProductORM
    from .users import UserORM


class ReviewORM(Base):
    __tablename__ = "reviews"
    __table_args__ = UniqueConstraint(
        "user_id", "product_id", name="unique_for_user_id_and_product_id"
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    comment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    grade: Mapped[int]
    is_active: Mapped[bool]
    user: Mapped["UserORM"] = relationship(back_populates="reviews")
    product: Mapped["ProductORM"] = relationship(back_populates="reviews")

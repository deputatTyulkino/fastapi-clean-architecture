from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


class UserRole(str, Enum):
    buyer = "buyer"
    admin = "admin"


class SellerStatus(str, Enum):
    pending = "pending"
    active = "active"
    suspended = "suspended"
    rejected = "rejected"


@dataclass
class SellerDomain:
    user_id: int
    store_name: str
    id: int | None = None
    description: str | None = None
    logo_url: str | None = None
    banner_url: str | None = None
    legal_name: str | None = None
    tax_id: str | None = None
    phone: str | None = None
    status: SellerStatus = SellerStatus.pending
    rejection_reason: str | None = None
    rating: Decimal = Decimal("0.0")
    reviews_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UserDomain:
    email: str
    hashed_password: str
    role: UserRole = UserRole.buyer
    id: int | None = None
    is_active: bool = True
    seller: SellerDomain | None = None

    @property
    def is_seller(self):
        return self.seller is not None

    @property
    def is_admin(self):
        return self.role == UserRole.admin


# Права:
# у админа: управление категориями, удаление товара и отзыва
#
# Давать возможность создания отзыва только после создания заказа

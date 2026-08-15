from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


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
    rating: Decimal = Decimal("0.0")
    reviews_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

    def filtered_none_fields(self):
        return asdict(
            self, dict_factory=lambda items: {k: v for k, v in items if v is not None}
        )

    def as_dict(self):
        return asdict(self)

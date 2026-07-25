from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from decimal import Decimal


@dataclass
class ProductDomain:
    name: str
    price: Decimal
    stock: int
    category_id: int
    seller_id: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: int | None = None
    description: str | None = None
    image_url: str | None = None
    is_active: bool = True
    rating: Decimal = Decimal(0)

    def filtered_none_fields(self):
        return asdict(
            self, dict_factory=lambda items: {k: v for k, v in items if v is not None}
        )

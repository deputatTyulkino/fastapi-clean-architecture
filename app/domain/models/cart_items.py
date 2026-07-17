from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class CartItemDomain:
    user_id: int
    product_id: int
    quantity: int = 1
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

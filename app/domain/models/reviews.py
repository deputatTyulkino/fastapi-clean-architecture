from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ReviewDomain:
    grade: int
    user_id: int
    product_id: int
    comment: str | None = None
    is_active: bool = True
    comment_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: int | None = None

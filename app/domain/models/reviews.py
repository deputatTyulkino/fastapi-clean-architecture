from dataclasses import asdict, dataclass, field
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

    def filtered_none_fields(self):
        return asdict(
            self, dict_factory=lambda items: {k: v for k, v in items if v is not None}
        )

    def as_dict(self):
        return asdict(self)

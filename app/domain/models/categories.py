from dataclasses import asdict, dataclass


@dataclass
class CategoryDomain:
    name: str
    id: int | None = None
    is_active: bool = True

    def filtered_none_fields(self):
        return asdict(
            self, dict_factory=lambda items: {k: v for k, v in items if v is not None}
        )

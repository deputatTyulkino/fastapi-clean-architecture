from dataclasses import dataclass


@dataclass
class CategoryDomain:
    name: str
    id: int | None = None
    is_active: bool = True

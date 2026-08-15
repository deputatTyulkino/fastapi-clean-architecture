from dataclasses import asdict, dataclass
from enum import Enum

from app.domain.models.sellers import SellerDomain


class UserRole(str, Enum):
    buyer = "buyer"
    admin = "admin"


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

    def as_dict(self):
        return asdict(self)

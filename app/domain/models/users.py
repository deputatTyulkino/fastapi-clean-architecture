from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    seller = "seller"
    buyer = "buyer"


@dataclass
class UserDomain:
    email: str
    hashed_password: str
    role: UserRole = UserRole.buyer
    id: int | None = None
    is_active: bool = True

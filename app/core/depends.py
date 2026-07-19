from app.core.auth import Security
from app.core.config import get_settings


def get_security() -> Security:
    settings = get_settings()
    return Security(settings)

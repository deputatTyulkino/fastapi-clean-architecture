from app.core.config import Settings, get_settings
from app.domain.interfaces.utils.i_token_services import ITokenServices
from app.infrastructure.utils.token_services import TokenServices


def get_token_services() -> ITokenServices:
    setting: Settings = get_settings()
    return TokenServices(setting)

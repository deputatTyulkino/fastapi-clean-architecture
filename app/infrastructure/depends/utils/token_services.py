from app.core.config import Settings, get_settings
from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.utils.i_token_services import ITokenServices
from app.infrastructure.logging.logger import get_logger
from app.infrastructure.utils.token_services import TokenServices


def get_token_services() -> ITokenServices:
    setting: Settings = get_settings()
    logger: ILogger = get_logger()
    return TokenServices(setting, logger)

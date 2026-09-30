from app.core.config import get_settings
from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.mail.i_mail_manager import IMailManager
from app.infrastructure.depends.utils.redis_depends import get_state_client
from app.infrastructure.logging.logger import get_logger
from app.infrastructure.mail.mail_manager import MailManager


def get_mail_manager() -> IMailManager:
    state_client = get_state_client()
    settings = get_settings()
    logger: ILogger = get_logger()
    return MailManager(state_client, settings, logger)

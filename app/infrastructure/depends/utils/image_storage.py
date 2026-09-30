from app.domain.interfaces.logging.i_logger import ILogger
from app.domain.interfaces.utils.i_image_storage import IImageServices
from app.infrastructure.logging.logger import get_logger
from app.infrastructure.utils.image_storage import ImageServices


def get_image_services() -> IImageServices:
    logger: ILogger = get_logger()
    return ImageServices(logger)

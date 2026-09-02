from app.domain.interfaces.utils.i_image_storage import IImageServices
from app.infrastructure.utils.image_storage import ImageServices


def get_image_services() -> IImageServices:
    return ImageServices()

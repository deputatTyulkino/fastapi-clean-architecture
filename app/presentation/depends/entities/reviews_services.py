from typing import Annotated

from fastapi import Depends

from app.application.services.reviews_services import ReviewServices
from app.infrastructure.depends.entities.users_services import get_users_services_infr


def get_reviews_services(
    services: Annotated[ReviewServices, Depends(get_users_services_infr)],
) -> ReviewServices:
    return services

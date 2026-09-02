from typing import Annotated

from fastapi import Depends

from app.application.services.users_services import UserServices
from app.infrastructure.depends.entities.users_services import get_users_services_infr


def get_users_servcies(
    services: Annotated[UserServices, Depends(get_users_services_infr)],
):
    return services

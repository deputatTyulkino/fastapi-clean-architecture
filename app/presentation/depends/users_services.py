from fastapi import Depends

from app.application.services.users_services import UserServices
from app.infrastructure.depends.users_services import get_users_services_infr


def get_users_servcies(services: UserServices = Depends(get_users_services_infr)):
    return services

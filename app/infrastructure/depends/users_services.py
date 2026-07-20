from fastapi import Depends

from app.application.services.users_services import UserServices
from app.core.auth import Security
from app.core.depends import get_security
from app.infrastructure.uow.depends import get_uow
from app.infrastructure.uow.uow import UnitOfWork


def get_users_services_infr(
    uow: UnitOfWork = Depends(get_uow), security: Security = Depends(get_security)
) -> UserServices:
    return UserServices(uow, security)

from fastapi import Depends, Request

from app.application.services.users_services import UserServices
from app.core.auth import Security
from app.core.depends import get_security
from app.infrastructure.uow.uow import UnitOfWork


def get_uow(request: Request):
    return UnitOfWork(request.app.state.session_factory)


def get_users_services_infr(
    uow: UnitOfWork = Depends(get_uow), security: Security = Depends(get_security)
):
    return UserServices(uow, security)

from typing import Annotated

from fastapi import Depends

from app.application.services.users_services import UserServices
from app.domain.interfaces.auth.i_refresh_token_repo import IRefreshTokenRepo
from app.domain.interfaces.utils.i_token_services import ITokenServices
from app.infrastructure.depends.utils.refresh_token_repo import get_refresh_token
from app.infrastructure.depends.utils.token_services import get_token_services
from app.infrastructure.uow.depends import get_uow_infr
from app.infrastructure.uow.uow import UnitOfWork


def get_users_services_infr(
    uow: Annotated[UnitOfWork, Depends(get_uow_infr)],
    token_services: Annotated[ITokenServices, Depends(get_token_services)],
    refresh_token_repo: Annotated[IRefreshTokenRepo, Depends(get_refresh_token)],
) -> UserServices:
    return UserServices(uow, token_services, refresh_token_repo)

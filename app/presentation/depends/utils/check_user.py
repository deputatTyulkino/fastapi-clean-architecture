from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.domain.interfaces.utils.i_token_services import ITokenServices
from app.domain.models.users import UserDomain
from app.infrastructure.depends.utils.token_services import get_token_services
from app.infrastructure.uow.uow import UnitOfWork
from app.presentation.depends.utils.uow import get_uow

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_schema)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
    token_services: Annotated[ITokenServices, Depends(get_token_services)],
) -> UserDomain:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Авторизуйтесь",
    )
    payload = token_services.decode_token(token)
    if payload is None:
        raise credentials_exception
    email: str | None = payload.get("sub")
    token_type: str | None = payload.get("token_type")
    if email is None or token_type != "access":
        raise credentials_exception
    async with uow:
        user = await uow.users.get_by_email(email)
        if user is None or not user.is_active:
            raise credentials_exception
    return user


def get_current_seller(
    user: Annotated[UserDomain, Depends(get_current_user)],
) -> UserDomain:
    if not user.is_seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав"
        )
    return user


def require_admin(
    user: Annotated[UserDomain, Depends(get_current_user)],
) -> None:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав"
        )

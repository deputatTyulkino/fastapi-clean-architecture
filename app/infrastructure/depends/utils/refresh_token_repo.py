from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.domain.interfaces.auth.i_refresh_token_repo import IRefreshTokenRepo
from app.domain.interfaces.logging.i_logger import ILogger
from app.infrastructure.auth.refresh_token_repo import RefreshTokenRepo
from app.infrastructure.depends.utils.redis_depends import get_state_client
from app.infrastructure.logging.logger import get_logger


def get_refresh_token(
    state_client: Annotated[Redis, Depends(get_state_client)],
    logger: Annotated[ILogger, Depends(get_logger)],
) -> IRefreshTokenRepo:
    return RefreshTokenRepo(state_client, 100, logger)

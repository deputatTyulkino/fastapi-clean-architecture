from fastapi import Request

from app.infrastructure.uow.uow import UnitOfWork


def get_uow(request: Request):
    return UnitOfWork(request.app.state.session_factory)

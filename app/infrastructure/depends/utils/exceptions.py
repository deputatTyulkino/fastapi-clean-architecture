from typing import Any


class HTTPError(Exception):
    """Базовая HTTP-ошибка (замена fastapi.HTTPException)."""

    status_code: int = 500
    default_detail: str = "Internal server error"

    def __init__(
        self,
        detail: Any = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.detail = detail if detail is not None else self.default_detail
        self.headers = headers
        super().__init__(str(self.detail))


class BadRequestHTTPError(HTTPError):
    status_code = 400
    default_detail = "Bad request"


class UnauthorizedHTTPError(HTTPError):
    status_code = 401
    default_detail = "Not authenticated"

    def __init__(
        self, detail: Any = None, headers: dict[str, str] | None = None
    ) -> None:
        headers = headers or {"WWW-Authenticate": "Bearer"}
        super().__init__(detail, headers)


class ForbiddenHTTPError(HTTPError):
    status_code = 403
    default_detail = "Forbidden"


class NotFoundHTTPError(HTTPError):
    status_code = 404
    default_detail = "Resource not found"


class ConflictHTTPError(HTTPError):
    status_code = 409
    default_detail = "Conflict"


class UnprocessableEntityHTTPError(HTTPError):
    status_code = 422
    default_detail = "Unprocessable entity"


class TooManyRequestsHTTPError(HTTPError):
    status_code = 429
    default_detail = "Too many requests"


class InternalServerHTTPError(HTTPError):
    status_code = 500
    default_detail = "Internal server error"

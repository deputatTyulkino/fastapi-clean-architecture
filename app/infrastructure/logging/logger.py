from __future__ import annotations

from typing import Any

import structlog

from app.domain.interfaces.logging.i_logger import ILogger


class StructlogLogger:
    def __init__(self, wrapped: Any | None = None) -> None:
        self._logger = wrapped if wrapped is not None else structlog.get_logger()

    def bind(self, **context: Any) -> "StructlogLogger":
        return StructlogLogger(self._logger.bind(**context))

    def debug(self, event: str, **kwargs: Any) -> None:
        self._logger.debug(event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:
        self._logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        self._logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        self._logger.error(event, **kwargs)

    def exception(self, event: str, **kwargs: Any) -> None:
        self._logger.exception(event, **kwargs)


def get_logger(**initial_context: Any) -> ILogger:
    return StructlogLogger(structlog.get_logger(**initial_context))

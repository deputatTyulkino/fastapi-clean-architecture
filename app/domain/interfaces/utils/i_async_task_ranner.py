import asyncio
from abc import ABC, abstractmethod
from collections.abc import Coroutine
from typing import Any


class IAsyncTaskRunner(ABC):
    @abstractmethod
    def get_loop() -> asyncio.AbstractEventLoop:
        raise NotImplementedError()

    @abstractmethod
    def _run_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        raise NotImplementedError()

    @abstractmethod
    def run(self, coro: Coroutine[Any, Any, None]) -> None:
        raise NotADirectoryError()

import asyncio
import threading
from collections.abc import Coroutine
from typing import Any

from app.domain.interfaces.utils.i_async_task_ranner import IAsyncTaskRunner


class AsyncTaskRunner(IAsyncTaskRunner):
    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._lock = threading.Lock()

    def get_loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is not None and self._loop.is_running():
            return self._loop

        with self._lock:
            self._loop = asyncio.new_event_loop()
            thread = threading.Thread(
                name="async_task_runner",
                target=self._run_loop,
                args=(self._loop,),
                daemon=True,
            )
            thread.start()
            return self._loop

    def _run_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def run(self, coro: Coroutine[Any, Any, None]) -> None:
        task = asyncio.run_coroutine_threadsafe(coro, self.get_loop())
        return task.result()

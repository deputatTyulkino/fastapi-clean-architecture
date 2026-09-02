from app.domain.interfaces.utils.i_async_task_ranner import IAsyncTaskRunner
from app.infrastructure.utils.async_task_runner import AsyncTaskRunner


def get_async_task_runner() -> IAsyncTaskRunner:
    return AsyncTaskRunner()

from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown

from app.core.config import get_settings
from app.infrastructure.celery import config
from app.infrastructure.depends.async_task_runner import get_async_task_runner
from app.infrastructure.depends.redis_depends import get_redis_manager_infr

settings = get_settings()
redis_manager = get_redis_manager_infr()
celery_app = Celery("ecommerce")
celery_app.config_from_object(config)
celery_app.autodiscover_tasks(["app.infrastructure.celery.tasks"])


@worker_process_init.connect
def init_worker_redis(**kwargs):
    async_runner = get_async_task_runner()
    async_runner.run(redis_manager.init())


@worker_process_shutdown.connect
def close_worker_redis(**kwargs):
    async_runner = get_async_task_runner()
    async_runner.run(redis_manager.close())

from app.application.services.rating_services import recalculate_products_rating
from app.infrastructure.celery.app import celery_app
from app.infrastructure.database.connect import session_factory
from app.infrastructure.depends.async_task_runner import get_async_task_runner
from app.infrastructure.uow.uow import UnitOfWork


@celery_app.task(
    name="products.recalculate_ratings",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def recalculate_rating_task(self, product_ids: list[int]) -> None:
    task_runner = get_async_task_runner()
    try:
        task_result = task_runner.run(
            recalculate_products_rating(UnitOfWork(session_factory), product_ids)
        )
        return task_result
    except Exception as exc:
        raise self.retry(exc=exc)

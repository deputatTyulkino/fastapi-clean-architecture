from app.infrastructure.celery.app import celery_app
from app.infrastructure.depends.utils.async_task_runner import get_async_task_runner
from app.infrastructure.depends.utils.mail_manager import get_mail_manager


@celery_app.task(name="mail.verify", bind=True, max_retries=3, default_retry_delay=5)
def verify_mail_task(self, email: str, code: str):
    task_runner = get_async_task_runner()
    mail_manager = get_mail_manager()
    try:
        task_runner.run(mail_manager.send_mail_for_verify(email, code))
    except Exception as exc:
        raise self.retry(exc=exc)

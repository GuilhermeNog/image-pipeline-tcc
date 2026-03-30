from celery import Celery

from app.config import settings

celery_app = Celery("image_pipeline", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_soft_time_limit=settings.JOB_TIMEOUT_SECONDS,
    task_time_limit=settings.JOB_TIMEOUT_SECONDS + 30,
)
celery_app.autodiscover_tasks(["app.workers"])

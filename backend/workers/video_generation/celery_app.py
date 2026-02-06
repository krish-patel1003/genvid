from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "video_generation_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["workers.video_generation.tasks", "workers.video_generation.upload_publish_video"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
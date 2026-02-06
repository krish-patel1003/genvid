import os
import httpx
from celery.utils.log import get_task_logger

from workers.video_generation.celery_app import celery_app
from workers.video_generation.generator import generate_video
from workers.video_generation.db import SessionLocal

from src.videos.models import VideoGenerationObject
from src.videos.enums import VideoStatusEnum
from src.videos.schemas import VideoGenerationObjectSchema
from src.core.config import get_settings

logger = get_task_logger(__name__)
settings = get_settings()

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 3},
)
def generate_video_task(self, generation_id: int):
    db = SessionLocal()
    video_gen_obj = None
    try:
        video_gen_obj = db.query(VideoGenerationObject).get(generation_id)
        if not video_gen_obj:
            return

        video_gen_obj.status = VideoStatusEnum.PROCESSING
        db.commit()

        output_path = generate_video(video_gen_obj.prompt, video_gen_obj.id)

        video_gen_obj.file_path = output_path
        video_gen_obj.status = VideoStatusEnum.READY
        db.commit()

        logger.info("Video generation completed.")
        _notify_video_generation(video_gen_obj)

    except Exception:
        if video_gen_obj:
            video_gen_obj.status = VideoStatusEnum.FAILED
            db.commit()
            _notify_video_generation(video_gen_obj)
        raise

    finally:
        db.close()


WS_NOTIFY_URL = settings.WS_NOTIFY_URL


def _build_notification_payload(video_gen_obj: VideoGenerationObject) -> dict:
    logger.info("Building notification payload...")
    data = VideoGenerationObjectSchema.model_validate(video_gen_obj).model_dump(mode="json")
    return {
        "type": "video_generation",
        "data": data,
    }


def _notify_video_generation(video_gen_obj: VideoGenerationObject) -> None:
    logger.info("Preparing to notify user about video generation status...")
    payload = _build_notification_payload(video_gen_obj)
    notify_user_task.delay(payload)


@celery_app.task
def notify_user_task(payload: dict):
    # try:
    #     print("Notifying WS server:", payload)
    #     httpx.post(WS_NOTIFY_URL, json=payload, timeout=2.0)
    # except Exception:
    #     # Best-effort notification; avoid failing the task.
    #     return

    logger.info("Notifying WS server: %s", payload)
    httpx.post(WS_NOTIFY_URL, json=payload, timeout=2.0)

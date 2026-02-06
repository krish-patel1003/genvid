from google.cloud import storage
from pathlib import Path
from datetime import timedelta
from fastapi import Depends

from src.videos.models import Video, VideoGenerationObject, VideoStatusEnum
from workers.video_generation.celery_app import celery_app
from workers.video_generation.db import SessionLocal
from src.core.dependencies import get_google_cloud_client
from src.auth.models import User

BUCKET_NAME = "genvid_videos_dev_v1"

def upload_to_object_storage(local_file_path: str, destination_blob_name: str) -> str:
    """Uploads a file to Google Cloud Storage and returns the public URL."""
    client = get_google_cloud_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(local_file_path)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=1),
        method="GET",
    )

    return url

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 5},
)
def upload_and_publish_video(self, generation_id: int, current_user_id: int):
    db = SessionLocal()

    try:
        gen = db.query(VideoGenerationObject).get(generation_id)
        if not gen or gen.status != VideoStatusEnum.READY:
            return

        # Upload to GCS
        blob_name = f"videos/{gen.id}.mp4"

        url = upload_to_object_storage(
            local_file_path=gen.file_path,
            destination_blob_name=blob_name,
        )

        # Create Video record
        video = Video(
            owner_id=current_user_id,
            video_url=url,
            status=VideoStatusEnum.PUBLISHED,
        )
        db.add(video)
        gen.status = VideoStatusEnum.PUBLISHED
        db.commit()

    except Exception:
        print("Error during upload and publish")
        gen.status = VideoStatusEnum.FAILED
        db.commit()
        raise

    finally:
        db.close()

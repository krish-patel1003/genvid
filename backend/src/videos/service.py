from sqlmodel import Session, select
from typing import Optional

from src.videos.models import Video, VideoGenerationJob
from src.videos.schema import GenerationCreate, VideoCreate, VideoPublic, VideosResponse
from src.videos.enums import GenerationStatus
from src.auth.models import User
from src.gcp.publisher import publish_generation_job
from src.gcp.storage import signed_get_url
from src.config import get_settings


def _signed_media_url(path: Optional[str], minutes: int = 30) -> Optional[str]:
    if not path:
        return None
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if path.startswith("gs://"):
        trimmed = path[len("gs://"):]
        bucket, _, object_name = trimmed.partition("/")
        if bucket and object_name:
            return signed_get_url(bucket, object_name, minutes=minutes)
    settings = get_settings()
    object_name = path.lstrip("/")
    if settings.GCS_BUCKET_NAME and object_name:
        path = signed_get_url(settings.GCS_BUCKET_NAME, object_name, minutes=minutes)
        print(f"Generated signed URL for {path}: {path}")
        return path
    return path

def create_video(data: VideoCreate, user: User, session: Session) -> Video:
    video = Video(
        caption=data.caption,
        user_id=user.id,
    )
    session.add(video)
    session.commit()
    session.refresh(video)

    return video


def list_user_videos(user: User, session: Session) -> list[Video]:
    videos = session.exec(
        select(Video).where(Video.user_id == user.id)
    ).all()

    # convert to VideoObject schema
    videos = [
        VideoPublic(
            id=v.id,
            owner_id=v.user_id,
            caption=v.caption,
            status=v.status,
            video_url=_signed_media_url(v.source_path),
            thumbnail_url=_signed_media_url(v.thumbnail_path),
            likes_count=v.likes_count,
            comments_count=v.comments_count,
            created_at=v.created_at,
            updated_at=v.updated_at,
        )
        for v in videos
    ]
    return VideosResponse(videos=videos)


def create_generation_task(
    data: GenerationCreate,
    session: Session,
    user: User,
) -> VideoGenerationJob:
    
    job = VideoGenerationJob(
        user_id=user.id,
        prompt=data.prompt,
        status=GenerationStatus.QUEUED,
    )

    session.add(job)
    session.commit()
    session.refresh(job)

    publish_generation_job(job.id)

    return job

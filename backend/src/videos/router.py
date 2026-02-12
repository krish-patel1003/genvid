from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlmodel import Session

from src.db import get_session
from src.videos.models import Video, VideoGenerationJob
from src.videos.schema import VideosResponse, VideoPublic
from src.auth.utils import get_current_user
from src.auth.models import User
from src.videos.service import list_user_videos
from src.videos.enums import GenerationStatus, VideoStatus
from src.gcp.storage import signed_get_url
from src.config import get_settings


router = APIRouter(prefix="/videos", tags=["videos"])

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
        return signed_get_url(settings.GCS_BUCKET_NAME, object_name, minutes=minutes)
    return path

@router.post("/{job_id}/publish")
def publish_generation(
    job_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    job = session.get(VideoGenerationJob, job_id)

    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != GenerationStatus.SUCCEEDED:
        raise HTTPException(status_code=400, detail="Job not publishable")
    if job.published_video_id:
        raise HTTPException(status_code=400, detail="Job already published")

    video = Video(
        user_id=user.id,
        caption=job.prompt,
        source_path=job.preview_video_path,
        processed_path=job.preview_video_path,
        thumbnail_path=job.preview_thumbnail_path,
        status=VideoStatus.READY,
    )

    session.add(video)
    session.flush()
    job.published_video_id = video.id
    session.add(job)
    session.commit()
    session.refresh(video)

    return {"video_id": video.id}

@router.get("/user-videos", response_model=VideosResponse)
def get_user_videos(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    response = list_user_videos(user=user, session=session)
    return response


@router.get("/{video_id}", response_model=VideoPublic)
def get_video(
    video_id: int,
    session: Session = Depends(get_session),
):
    video = session.get(Video, video_id)
    if not video or video.status != VideoStatus.READY:
        raise HTTPException(status_code=404, detail="Video not found")

    source_path = video.processed_path or video.source_path

    return VideoPublic(
        id=video.id,
        owner_id=video.user_id,
        caption=video.caption,
        status=video.status,
        video_url=_signed_media_url(source_path),
        thumbnail_url=_signed_media_url(video.thumbnail_path),
        likes_count=video.likes_count,
        comments_count=video.comments_count,
        created_at=video.created_at,
        updated_at=video.updated_at,
    )


@router.get("/{job_id}/preview-urls")
def get_preview_urls(
    job_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    job = session.get(VideoGenerationJob, job_id)
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != GenerationStatus.SUCCEEDED:
        raise HTTPException(status_code=400, detail="Preview not available yet")

    if not job.preview_video_path:
        raise HTTPException(status_code=500, detail="Preview object missing")

    return {
        "preview_video_url": _signed_media_url(job.preview_video_path, minutes=30),
        "preview_thumbnail_url": _signed_media_url(job.preview_thumbnail_path, minutes=30),
    }

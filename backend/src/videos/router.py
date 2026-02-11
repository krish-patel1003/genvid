from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from src.db import get_session
from src.videos.models import Video, VideoGenerationJob
from src.videos.schema import VideoCreate, VideoRead
from src.auth.utils import get_current_user
from src.auth.models import User
from src.videos.service import create_video, list_user_videos
from src.videos.schema import GenerationCreate, GenerationRead
from src.videos.service import create_generation_task
from src.videos.enums import GenerationStatus
from src.gcp.storage import signed_get_url


router = APIRouter(prefix="/videos", tags=["videos"])

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

    video = Video(
        owner_id=user.id,
        caption=job.prompt,
        video_url=job.preview_video_path,
        thumbnail_url=job.preview_thumbnail_path,
        status="READY",
    )

    session.add(video)

    # finalize job
    job.status = GenerationStatus.DISCARDED
    session.add(job)

    session.commit()
    session.refresh(video)

    return {"video_id": video.id}


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

    if not job.preview_video_object:
        raise HTTPException(status_code=500, detail="Preview object missing")

    return {
        "preview_video_url": signed_get_url(job.preview_video_object, expires_minutes=30),
        "preview_thumbnail_url": (
            signed_get_url(job.preview_thumbnail_object, expires_minutes=30)
            if job.preview_thumbnail_object else None
        ),
    }

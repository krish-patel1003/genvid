from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from src.db import get_session
from src.videos.models import Video, VideoGenerationJob
from src.videos.schema import VideoCreate, VideoObject, VideosResponse
from src.auth.utils import get_current_user
from src.auth.models import User
from src.videos.service import create_video, list_user_videos
from src.videos.schema import GenerationCreate, GenerationRead
from src.videos.service import create_generation_task
from src.videos.enums import GenerationStatus, VideoStatus
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
        user_id=user.id,
        caption=job.prompt,
        processed_path=job.preview_video_path,
        thumbnail_path=job.preview_thumbnail_path,
        status=VideoStatus.READY,
    )

    session.add(video)

    # # finalize job
    # job.status = GenerationStatus.
    # session.add(job)

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
        "preview_video_url": signed_get_url(job.preview_video_path, expires_minutes=30),
        "preview_thumbnail_url": (
            signed_get_url(job.preview_thumbnail_path, expires_minutes=30)
            if job.preview_thumbnail_path else None
        ),
    }

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from datetime import datetime, timezone
from sqlmodel import select, func

from src.auth.utils import get_current_user
from src.db import get_session
from src.gcp.publisher import publish_generation_job
from src.videos.enums import GenerationStatus
from src.videos.generation.schema import (
    VideoGenerationJob as VideoGenerationJobSchema,
    VideoGenerationRequest,
    VideoGenerationResponse,
)
from src.videos.models import VideoGenerationJob as VideoGenerationJobModel


router = APIRouter(prefix="/video-generation", tags=["video-generation"])

MAX_GENERATIONS_PER_DAY = 2
# TODO: validate prompt length
@router.post("/generate", response_model=VideoGenerationResponse)
def generate(
    data: VideoGenerationRequest,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    # Check if user has exceeded daily generation limit
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    count = session.exec(
        select(func.count())
        .where(
            VideoGenerationJobModel.user_id == current_user.id,
            VideoGenerationJobModel.created_at >= today_start,
        )
    ).one()

    if count >= MAX_GENERATIONS_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail="Daily generation limit reached (2 per day)."
        )

    if count >= MAX_GENERATIONS_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail="Daily generation limit reached (2 per day)."
        )

    job = VideoGenerationJobModel(
        user_id=current_user.id,
        prompt=data.prompt,
        status=GenerationStatus.QUEUED,
    )

    session.add(job)
    session.commit()
    session.refresh(job)

    publish_generation_job({
        "job_id": job.id,
        "prompt": data.prompt
    })

    return {"job_id": job.id, "status": job.status}


@router.get("/{job_id}", response_model=VideoGenerationJobSchema)
def get_generation_status(
    job_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    job = session.get(VideoGenerationJobModel, job_id)

    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    return job

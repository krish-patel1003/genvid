import mimetypes
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session
from datetime import datetime, timezone
from sqlmodel import select, func

from src.auth.utils import get_current_user
from src.db import get_session
from src.gcp.publisher import publish_generation_job
from src.gcp.storage import upload_upload_file_to_bucket, delete_object
from src.config import get_settings
from src.videos.enums import GenerationStatus
from src.videos.generation.schema import (
    VideoGenerationJob as VideoGenerationJobSchema,
    VideoGenerationResponse,
)
from src.videos.models import VideoGenerationJob as VideoGenerationJobModel


router = APIRouter(prefix="/video-generation", tags=["video-generation"])
settings = get_settings()

MAX_GENERATIONS_PER_DAY = 2
MAX_REFERENCE_IMAGES = 3
MAX_REFERENCE_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_REFERENCE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def _validate_reference_images(reference_images: list[UploadFile]) -> None:
    if len(reference_images) > MAX_REFERENCE_IMAGES:
        raise HTTPException(
            status_code=400,
            detail=f"You can upload up to {MAX_REFERENCE_IMAGES} reference images.",
        )

    for image in reference_images:
        if image.content_type not in ALLOWED_REFERENCE_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only JPEG, PNG, and WEBP reference images are supported.",
            )

        image.file.seek(0, 2)
        size = image.file.tell()
        image.file.seek(0)
        if size > MAX_REFERENCE_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail="Each reference image must be 10MB or smaller.",
            )


@router.post("/generate", response_model=VideoGenerationResponse)
def generate(
    prompt: str = Form(...),
    reference_images: list[UploadFile] = File(default=[]),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    prompt = prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required.")

    _validate_reference_images(reference_images)

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

    job = VideoGenerationJobModel(
        user_id=current_user.id,
        prompt=prompt,
        reference_image_paths=[],
        status=GenerationStatus.QUEUED,
    )

    session.add(job)
    session.commit()
    session.refresh(job)

    uploaded_paths: list[str] = []
    try:
        for image in reference_images:
            ext = mimetypes.guess_extension(image.content_type or "") or ".jpg"
            blob_name = f"references/{current_user.id}/{job.id}/{uuid4().hex}{ext}"
            uploaded_path = upload_upload_file_to_bucket(
                bucket_name=settings.GCS_BUCKET_NAME,
                destination_blob_name=blob_name,
                file=image,
            )
            uploaded_paths.append(uploaded_path)

        job.reference_image_paths = uploaded_paths
        session.add(job)
        session.commit()
        session.refresh(job)
    except Exception:
        for path in uploaded_paths:
            try:
                delete_object(settings.GCS_BUCKET_NAME, path)
            except Exception:
                pass
        session.delete(job)
        session.commit()
        raise

    publish_generation_job({
        "job_id": job.id,
        "prompt": prompt,
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

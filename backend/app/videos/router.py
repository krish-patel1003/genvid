from fastapi import APIRouter, Depends, Request, HTTPException

from app.core.dependencies import get_db, get_current_user
from app.videos.schemas import VideoUploadSchema
from app.videos.services import create_video_record

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/")
def upload_video(
    data: VideoUploadSchema,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    

    video = create_video_record(
        title=data.title,
        description=data.description,
        file_path=data.file_path,
        owner=current_user,
        db=db,
    )
    return video
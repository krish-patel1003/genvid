from fastapi import APIRouter, Depends, Request, HTTPException

from app.core.dependencies import get_db, get_current_user
from app.videos.schemas import VideoUploadSchema, VideoPublicSchema
from app.videos.services import create_video_record, get_video_by_id, delete_video_record, get_videos_by_owner
from app.videos.models import Video

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/")
def upload_video(
    data: VideoUploadSchema,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    

    video = create_video_record(
        caption=data.caption,
        owner_id=current_user.id,
        db=db,
    )
    return video


@router.get("/{video_id}", response_model=VideoPublicSchema)
def get_video(
    video_id: int,
    db=Depends(get_db),
):
    
    video = get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.delete("/{video_id}", status_code=204)
def delete_video(
    video_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    video = get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this video")

    delete_video_record(db, video)
    return

@router.get("/user/videos", response_model=list[VideoPublicSchema])
def get_user_videos(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    videos = get_videos_by_owner(db, current_user)
    return videos
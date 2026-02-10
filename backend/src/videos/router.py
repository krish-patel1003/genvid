from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from src.db import get_session
from src.videos.models import Video
from src.videos.schema import VideoCreate, VideoRead
from src.auth.utils import get_current_user
from src.auth.models import User
from src.videos.service import create_video, list_user_videos

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/", response_model=VideoRead)
def create_video(
    data: VideoCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    
    video = create_video(data, user, session)
    return video
    

@router.get("/", response_model=list[VideoRead])
def list_my_videos(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    videos = list_user_videos(user, session)  
    return videos

@router.get("/{video_id}", response_model=VideoRead)
def get_video(
    video_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    video = session.get(Video, video_id)
    if not video or video.user_id != user.id:
        raise HTTPException(status_code=404, detail="Video not found")

    return video



from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.videos.models import VideoStatus, GenerationStatus
from src.videos.enums import VideoStatus, GenerationStatus


class VideoCreate(BaseModel):
    caption: Optional[str] = None


class VideoObject(BaseModel):
    id: int
    user_id: int
    caption: Optional[str] = None
    status: VideoStatus
    source_path: Optional[str] = None
    processed_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    likes_count: int
    comments_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class VideoPublic(BaseModel):
    id: int
    owner_id: int
    caption: Optional[str] = None
    status: VideoStatus
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    likes_count: int
    comments_count: int
    created_at: datetime
    updated_at: datetime

class VideosResponse(BaseModel):
    videos: list[VideoPublic]

class GenerationCreate(BaseModel):
    prompt: str


class GenerationRead(BaseModel):
    id: int
    user_id: int
    prompt: str
    status: GenerationStatus
    preview_video_path: Optional[str]
    preview_thumbnail_path: Optional[str]
    error_message: Optional[str]
    published_video_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

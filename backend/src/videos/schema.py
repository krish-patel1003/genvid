from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.videos.models import VideoStatus, GenerationStatus
from src.videos.enums import VideoStatus, GenerationStatus


class VideoCreate(BaseModel):
    caption: Optional[str] = None


class VideoRead(BaseModel):
    id: int
    caption: Optional[str]
    status: VideoStatus
    created_at: datetime

    class Config:
        orm_mode = True


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
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

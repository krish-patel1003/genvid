from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.videos.models import VideoStatus


class VideoCreate(BaseModel):
    title: str
    description: Optional[str] = None


class VideoRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: VideoStatus
    created_at: datetime

    class Config:
        orm_mode = True

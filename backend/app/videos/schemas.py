from pydantic import BaseModel
from typing import Optional


class VideoUploadSchema(BaseModel):
    caption: Optional[str] = None


class VideoPublicSchema(BaseModel):
    id: Optional[int] = None
    owner_id: Optional[int] = None
    status: Optional[str] = None
    caption: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True  # pydantic v2


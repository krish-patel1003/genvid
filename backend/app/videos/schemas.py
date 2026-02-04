from pydantic import BaseModel
from typing import Optional


class VideoUploadSchema(BaseModel):
    caption: Optional[str] = None


class VideoPublicSchema(BaseModel):
    id: int
    owner_id: int
    status: str
    caption: Optional[str] = None
    video_url: str
    thumbnail_url: str
    created_at: str

    class Config:
        from_attributes = True  # pydantic v2


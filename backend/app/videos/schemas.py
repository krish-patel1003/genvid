from datetime import datetime
from pydantic import BaseModel, field_serializer
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
    created_at: Optional[datetime] = None

    @field_serializer("created_at")
    def _serialize_datetime(self, value: Optional[datetime]):
        if value is None:
            return None
        return value.isoformat()
    
    class Config:
        from_attributes = True  # pydantic v2


class VideoGenerationCreateSchema(BaseModel):
    prompt: str

class VideoGenerationObjectSchema(BaseModel):
    id: Optional[int] = None
    video_id: Optional[int] = None
    prompt: Optional[str] = None
    file_path: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer("created_at", "updated_at")
    def _serialize_datetime(self, value: Optional[datetime]):
        if value is None:
            return None
        return value.isoformat()

    class Config:
        from_attributes = True  # pydantic v2

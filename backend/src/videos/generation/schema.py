from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VideoGenerationRequest(BaseModel):
    prompt: str

class VideoGenerationResponse(BaseModel):
    job_id: int
    status: str

class VideoGenerationJob(BaseModel):
    id: int
    user_id: int
    prompt: str
    reference_image_paths: list[str] = Field(default_factory=list)
    status: str
    created_at: datetime
    updated_at: datetime
    preview_video_path: Optional[str] = None
    preview_thumbnail_path: Optional[str] = None
    error_message: Optional[str] = None
    published_video_id: Optional[int] = None

    model_config = {"from_attributes": True}

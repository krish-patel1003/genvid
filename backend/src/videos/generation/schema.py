from pydantic import BaseModel
from typing import Optional


class VideoGenerationRequest(BaseModel):
    prompt: str

class VideoGenerationResponse(BaseModel):
    job_id: int
    status: str

class VideoGenerationJob(BaseModel):
    id: int
    user_id: int
    prompt: str
    status: str
    created_at: str
    updated_at: Optional[str] = None
    preview_video_object: Optional[str] = None
    preview_thumbnail_object: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        orm_mode = True
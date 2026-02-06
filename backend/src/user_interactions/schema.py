from pydantic import BaseModel, field_serializer
from typing import List, Optional
from datetime import datetime

class PostCommentSchema(BaseModel):
    video_id: int
    comment_text: str
    parent_comment_id: Optional[int] = None

class CommentSchema(BaseModel):
    video_id: int
    content: str
    parent_comment_id: Optional[int] = None
    created_at: Optional[datetime] = None

    @field_serializer("created_at")
    def _serialize_datetime(self, value: Optional[datetime]):
        if value is None:
            return None
        return value.isoformat()

    class Config:
        from_attributes = True  # pydantic v2
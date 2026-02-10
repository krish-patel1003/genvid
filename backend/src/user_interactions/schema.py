from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime


class PostCommentSchema(BaseModel):
    comment_text: str
    parent_comment_id: Optional[int] = None


class CommentSchema(BaseModel):
    id: int
    video_id: int
    content: str
    parent_comment_id: Optional[int] = None
    created_at: Optional[datetime] = None

    @field_serializer("created_at")
    def serialize_datetime(self, value: Optional[datetime]):
        return value.isoformat() if value else None

    model_config = {
        "from_attributes": True
    }

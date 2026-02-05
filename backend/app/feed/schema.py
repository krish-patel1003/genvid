from pydantic import BaseModel, field_serializer
from typing import List, Optional

class FeedItemSchema(BaseModel):
    video_id: int
    owner_username: str
    owner_profile_pic: Optional[str] = None
    caption: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    # likes_count: int
    # comments_count: int
    # is_liked_by_user: bool
    created_at: Optional[str] = None

    # @field_serializer("created_at")
    # def _serialize_datetime(self, value: Optional[str]):
    #     if value is None:
    #         return None
    #     return value.isoformat()

    class Config:
        from_attributes = True  # pydantic v2

class FeedSchema(BaseModel):
    items: Optional[List[FeedItemSchema]] = []
    next_page_token: Optional[str] = None
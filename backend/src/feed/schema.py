from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FeedItemSchema(BaseModel):
    video_id: int
    owner_username: str
    owner_profile_pic: Optional[str]
    caption: Optional[str]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    likes_count: int
    comments_count: int
    is_liked_by_user: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedSchema(BaseModel):
    items: List[FeedItemSchema]
    next_page_token: Optional[str] = None

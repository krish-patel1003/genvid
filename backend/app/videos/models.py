from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from app.core.db import Base
from app.videos.enums import VideoStatusEnum
from datetime import datetime, timezone

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(ForeignKey("users.id"), nullable=False, index=True)

    status = Column(Enum(VideoStatusEnum), nullable=False, default=VideoStatusEnum.DRAFT)

    caption = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)

    created_at = Column(String, nullable=False, default=datetime.now(timezone.utc).isoformat())
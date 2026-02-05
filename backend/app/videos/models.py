from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime
from datetime import datetime, timezone
from app.core.db import Base
from app.videos.enums import VideoStatusEnum


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(ForeignKey("users.id"), nullable=False, index=True)

    caption = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)

    status = Column(
        Enum("DRAFT", "PUBLISHED", name="video_publish_status"),
        nullable=False,
        default="DRAFT",
    )

    likes_count = Column(Integer, nullable=True, default=0)

    comments_count = Column(Integer, nullable=True, default=0)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class VideoGenerationObject(Base):
    __tablename__ = "video_generation_objects"

    id = Column(Integer, primary_key=True, index=True)
    
    prompt = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)

    status = Column(
        Enum(VideoStatusEnum),
        nullable=False,
        default=VideoStatusEnum.DRAFT,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


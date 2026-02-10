from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
import sqlalchemy as sa

from src.videos.enums import VideoStatus, GenerationStatus

class Video(SQLModel, table=True):
    __tablename__ = "videos"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id", index=True)

    title: str
    description: Optional[str] = None

    status: VideoStatus = Field(default=VideoStatus.PENDING, index=True)

    source_path: Optional[str] = None
    processed_path: Optional[str] = None
    thumbnail_path: Optional[str] = None

    likes_count: int = Field(default=0)
    comments_count: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc), sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'onupdate': sa.func.now(),
            'server_default': sa.func.now(),
        }
    )

    # owner: Optional["User"] = Relationship(back_populates="videos")


class VideoGenerationJob(SQLModel, table=True):
    __tablename__ = "video_generation_jobs"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id", index=True)

    prompt: str

    status: GenerationStatus = Field(default=GenerationStatus.QUEUED, index=True)

    # preview artifacts
    preview_video_path: Optional[str] = None
    preview_thumbnail_path: Optional[str] = None

    # failure info
    error_message: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc), sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'onupdate': sa.func.now(),
            'server_default': sa.func.now(),
        }
    )

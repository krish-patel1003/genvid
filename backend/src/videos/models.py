from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
import sqlalchemy as sa


class VideoStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


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

    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc), sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'onupdate': sa.func.now(),
            'server_default': sa.func.now(),
        }
    )

    # owner: Optional["User"] = Relationship(back_populates="videos")

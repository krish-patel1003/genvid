from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.schema import UniqueConstraint
from datetime import datetime, timezone
from src.core.db import Base

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    video_id = Column(ForeignKey("videos.id"), nullable=False, index=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        # Ensure a user can like a video only once
        UniqueConstraint('user_id', 'video_id', name='uq_user_video_like'),
    )



class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    parent_comment_id = Column(ForeignKey("comments.id"), nullable=True, index=True)
    video_id = Column(ForeignKey("videos.id"), nullable=False, index=True)
    content = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
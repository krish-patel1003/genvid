from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.core.db import Base
from typing import Enum


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(ForeignKey("users.id"), nullable=False, index=True)

    status = Column(
        Enum("DRAFT", "PROCESSING", "READY", "PUBLISHED", "FAILED", name="video_status"),
        Default="DRAFT",
        nullable=False,
    )

    caption = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)

    created_at = Column(String, nullable=False)
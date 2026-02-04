from sqlalchemy import UniqueConstraint, Column, Integer, String, ForeignKey
from datetime import datetime, timezone

from app.core.db import Base

class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False, index=True)
    followed_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False, index=True)
    created_at = Column(String, nullable=False, default=lambda: datetime.now(timezone.utc).isoformat())

    
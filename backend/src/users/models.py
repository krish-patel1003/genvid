from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Follow(SQLModel, table=True):
    __tablename__ = "follows"

    follower_id: int = Field(foreign_key="users.id", primary_key=True, index=True)
    followed_id: int = Field(foreign_key="users.id", primary_key=True, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
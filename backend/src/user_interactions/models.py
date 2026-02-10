from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Like(SQLModel, table=True):
    __tablename__ = "likes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    video_id: int = Field(foreign_key="videos.id", index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    video_id: int = Field(foreign_key="videos.id", index=True)
    parent_comment_id: Optional[int] = Field(default=None, foreign_key="comments.id")

    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

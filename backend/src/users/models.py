from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import sqlalchemy as sa

from src.datetime_utils import utcnow



class Follow(SQLModel, table=True):
    __tablename__ = "follows"

    follower_id: int = Field(foreign_key="users.id", primary_key=True, index=True)
    followed_id: int = Field(foreign_key="users.id", primary_key=True, index=True)

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": sa.func.now(),
        },
    )

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from typing import Optional, List
from datetime import datetime, timezone
from src.datetime_utils import utcnow
import sqlalchemy as sa


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    username: str = Field(index=True, unique=True)

    hashed_password: Optional[str] = None
    profile_pic: Optional[str] = None
    bio: Optional[str] = None

    created_at: datetime = Field(
        default_factory=utcnow,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": sa.func.now(),
        },
    )

    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": sa.func.now(),
            "onupdate": sa.func.now(),
        },
    )

    oauth_accounts: List["OAuthAccount"] = Relationship(back_populates="user")


class OAuthAccount(SQLModel, table=True):
    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_user"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")

    provider: str
    provider_user_id: str

    user: "User" = Relationship(back_populates="oauth_accounts")

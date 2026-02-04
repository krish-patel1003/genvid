from app.core.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import ForeignKey, UniqueConstraint


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False) 
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # required for OAuth
    profile_pic = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)


class OAuthAccount(Base):
    
    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)
    provider_user_id = Column(String, nullable=False)


    __table_args__ = (
        UniqueConstraint('provider', provider_user_id, name='uq_provider_user'),
    )
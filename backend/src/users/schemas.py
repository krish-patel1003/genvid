from pydantic import BaseModel, EmailStr
from typing import Optional


class UserPublicSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    bio: Optional[str] = None
    profile_pic: Optional[str] = None

    model_config = {
        "from_attributes": True  # pydantic v2
    }


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None

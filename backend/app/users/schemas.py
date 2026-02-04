from pydantic import BaseModel, EmailStr
from typing import Optional


class UserPublicSchema(BaseModel):
    id: Optional[int] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    profile_pic: Optional[str] = None 

    class Config:
        from_attributes = True  # pydantic v2
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SignupSchema(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=256)  # argon2 can handle long passwords

from pydantic import BaseModel


class SignupSchema(BaseModel):
    email: str
    username: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

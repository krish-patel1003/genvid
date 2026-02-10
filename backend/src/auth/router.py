from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.security import create_access_token
from src.auth_util import get_current_user
from src.auth.schema import LoginRequest, TokenResponse


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    # Stub user identity (DB comes later)
    token = create_access_token(subject=request.email)
    return TokenResponse(access_token=token)


@router.get("/me")
def me(user = Depends(get_current_user)):
    return {"user": user}
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlmodel import Session

from src.db import get_session
from src.auth.utils import get_current_user
from src.auth.models import User
from src.users.schemas import UserPublicSchema, UserUpdateSchema
from src.users.services import (
    update_user,
    upload_profile_picture,
    follow_user,
    unfollow_user,
    get_followers,
    get_following,
)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserPublicSchema)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserPublicSchema)
def update_me(
    data: UserUpdateSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return update_user(user=current_user, data=data, session=session)


@router.post("/me/profile-pic", response_model=UserPublicSchema)
def update_profile_pic(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return upload_profile_picture(
        user=current_user,
        file=file,
        session=session,
    )


@router.post("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    follow_user(
        target_user_id=user_id,
        current_user=current_user,
        session=session,
    )


@router.delete("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    unfollow_user(
        target_user_id=user_id,
        current_user=current_user,
        session=session,
    )


@router.get("/{user_id}/followers", response_model=list[UserPublicSchema])
def followers(
    user_id: int,
    session: Session = Depends(get_session),
):
    return get_followers(user_id=user_id, session=session)


@router.get("/{user_id}/following", response_model=list[UserPublicSchema])
def following(
    user_id: int,
    session: Session = Depends(get_session),
):
    return get_following(user_id=user_id, session=session)



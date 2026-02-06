from fastapi import APIRouter, Depends, UploadFile, File

from src.core.dependencies import get_db, get_current_user
from src.users.schemas import UserPublicSchema, UserUpdateSchema
from src.users.services import update_user, follow, unfollow, get_followers, get_following, upload_profile_picture


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserPublicSchema)
def me(current_user=Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserPublicSchema)
def update_me(
    data: UserUpdateSchema,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    updated_user = update_user(
        user=current_user,
        username=data.username,
        bio=data.bio,
        profile_pic=data.profile_pic,
        db=db,
    )
    return updated_user

@router.post("/me/profile-pic", response_model=UserPublicSchema)
def update_profile_pic(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    updated_user = upload_profile_picture(
        user=current_user,
        file=file,
        db=db,
    )
    return updated_user

@router.post("/{user_id}/follow", status_code=204)
def follow_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    follow(
        target_user_id=user_id,
        current_user=current_user,
        db=db,
    )
    return

@router.delete("/{user_id}/follow", status_code=204)
def unfollow_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    unfollow(
        target_user_id=user_id,
        current_user=current_user,
        db=db,
    )
    return

@router.get("/{user_id}/followers", response_model=list[UserPublicSchema])
def get_user_followers(
    user_id: int,
    db=Depends(get_db),
):
    followers = get_followers(user_id=user_id, db=db)
    return followers


@router.get("/{user_id}/following", response_model=list[UserPublicSchema])
def get_user_following(
    user_id: int,
    db=Depends(get_db),
):
    following = get_following(user_id=user_id, db=db)
    return following

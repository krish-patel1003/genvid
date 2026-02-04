from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_db, get_current_user
from app.users.schemas import UserPublicSchema
from app.users.services import follow, unfollow, get_followers, get_following


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserPublicSchema)
def me(current_user=Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserPublicSchema)
def update_me(
    data: UserPublicSchema,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    user = db.query(current_user.__class__).filter(current_user.__class__.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}/follow", status_code=204)
def follow_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    follow(
        user_id=user_id,
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
        user_id=user_id,
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
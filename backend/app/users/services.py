from fastapi import Depends, HTTPException

from app.auth.models import User
from app.users.models import Follow
from app.core.dependencies import get_current_user, get_db, user_exists


def follow(
        user_id: int,
        current_user=Depends(get_current_user),
        db=Depends(get_db),
    ):

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    if not user_exists(user_id=user_id, db=db):
        raise HTTPException(status_code=404, detail="User not found")
    
    follow_relation = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followed_id == user_id
    ).first()

    if follow_relation:
        raise HTTPException(status_code=400, detail="Already following this user")
    
    new_follow = Follow(follower_id=current_user.id, followed_id=user_id)
    db.add(new_follow)
    db.commit()
    return


def unfollow(
        user_id: int,
        current_user=Depends(get_current_user),
        db=Depends(get_db),
    ):

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot unfollow yourself")
    
    follow_relation = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followed_id == user_id
    ).first()

    if not follow_relation:
        raise HTTPException(status_code=400, detail="Not following this user")
    
    db.delete(follow_relation)
    db.commit()
    return


def get_followers(user_id: int, db=Depends(get_db)):

    # Verify user exists
    if not user_exists(user_id=user_id, db=db):
        raise HTTPException(status_code=404, detail="User not found")
    
    followers = db.query(User).join(Follow, Follow.follower_id == User.id).filter(
        Follow.followed_id == user_id
    ).all()
    return followers


def get_following(user_id: int, db=Depends(get_db)):
    
    # Verify user exists
    if not user_exists(user_id=user_id, db=db):
        raise HTTPException(status_code=404, detail="User not found")
    
    following = db.query(User).join(Follow, Follow.followed_id == User.id).filter(
        Follow.follower_id == user_id
    ).all()
    return following




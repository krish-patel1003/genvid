from fastapi import Depends, HTTPException

from app.auth.models import User
from app.users.models import Follow


def follow(
    *,
    target_user_id: int,
    current_user: User,
    db,
):
    if target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    exists = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followed_id == target_user_id,
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Already following this user")

    db.add(
        Follow(
            follower_id=current_user.id,
            followed_id=target_user_id,
        )
    )
    db.commit()


def unfollow(
        *,
        target_user_id: int,
        current_user: User,
        db,
    ):

    if target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot unfollow yourself")
    
    follow_relation = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followed_id == target_user_id
    ).first()

    if not follow_relation:
        raise HTTPException(status_code=400, detail="Not following this user")
    
    db.delete(follow_relation)
    db.commit()
    return


def get_followers(user_id: int, db):
    followers = db.query(User).join(
        Follow, Follow.follower_id == User.id
    ).filter(
        Follow.followed_id == user_id
    ).all()
    return followers

def get_following(user_id: int, db):
    following = db.query(User).join(
        Follow, Follow.followed_id == User.id
    ).filter(
        Follow.follower_id == user_id
    ).all()
    return following



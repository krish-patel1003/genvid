import os
import shutil
import tempfile
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from sqlmodel import Session, select

from src.auth.models import User
from src.users.models import Follow
from src.gcp.storage import get_gcs_client, generate_presigned_url

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

def update_user(
    *,
    user: User,
    data,
    session: Session,
) -> User:
    if data.username is not None:
        user.username = data.username

    if data.bio is not None:
        user.bio = data.bio

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def upload_profile_picture(
    *,
    user: User,
    file: UploadFile,
    session: Session,
) -> User:
    suffix = os.path.splitext(file.filename or "")[1] or ".jpg"
    blob_name = f"profile_pics/{user.id}/{uuid4().hex}{suffix}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        client = get_gcs_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)

        blob.upload_from_filename(
            tmp_path,
            content_type=file.content_type,
        )

        url = generate_presigned_url(BUCKET_NAME, blob_name)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    user.profile_pic = url
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def follow_user(
    *,
    target_user_id: int,
    current_user: User,
    session: Session,
):
    if target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    target = session.get(User, target_user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    stmt = select(Follow).where(
        Follow.follower_id == current_user.id,
        Follow.followed_id == target_user_id,
    )
    exists = session.exec(stmt).first()

    if exists:
        raise HTTPException(status_code=400, detail="Already following this user")

    session.add(
        Follow(
            follower_id=current_user.id,
            followed_id=target_user_id,
        )
    )
    session.commit()


def unfollow_user(
    *,
    target_user_id: int,
    current_user: User,
    session: Session,
):
    if target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot unfollow yourself")

    stmt = select(Follow).where(
        Follow.follower_id == current_user.id,
        Follow.followed_id == target_user_id,
    )
    relation = session.exec(stmt).first()

    if not relation:
        raise HTTPException(status_code=400, detail="Not following this user")

    session.delete(relation)
    session.commit()


def get_followers(user_id: int, session: Session):
    stmt = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.followed_id == user_id)
    )
    return session.exec(stmt).all()


def get_following(user_id: int, session: Session):
    stmt = (
        select(User)
        .join(Follow, Follow.followed_id == User.id)
        .where(Follow.follower_id == user_id)
    )
    return session.exec(stmt).all()

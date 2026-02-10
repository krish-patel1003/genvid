from sqlmodel import Session, select
from sqlalchemy import update

from src.user_interactions.models import Like, Comment
from src.videos.models import Video


def like_video(*, session: Session, user_id: int, video_id: int) -> bool:
    exists = session.exec(
        select(Like).where(
            Like.user_id == user_id,
            Like.video_id == video_id,
        )
    ).first()

    if exists:
        return False

    session.add(Like(user_id=user_id, video_id=video_id))
    session.exec(
        update(Video)
        .where(Video.id == video_id)
        .values(likes_count=Video.likes_count + 1)
    )
    session.commit()
    return True


def unlike_video(*, session: Session, user_id: int, video_id: int) -> bool:
    like = session.exec(
        select(Like).where(
            Like.user_id == user_id,
            Like.video_id == video_id,
        )
    ).first()

    if not like:
        return False

    session.delete(like)
    session.exec(
        update(Video)
        .where(Video.id == video_id, Video.likes_count > 0)
        .values(likes_count=Video.likes_count - 1)
    )
    session.commit()
    return True


def comment_on_video(
    *,
    session: Session,
    user_id: int,
    video_id: int,
    content: str,
    parent_comment_id: int | None = None,
) -> Comment:
    comment = Comment(
        user_id=user_id,
        video_id=video_id,
        content=content,
        parent_comment_id=parent_comment_id,
    )
    session.add(comment)

    session.exec(
        update(Video)
        .where(Video.id == video_id)
        .values(comments_count=Video.comments_count + 1)
    )

    session.commit()
    session.refresh(comment)
    return comment


def get_comments_data(*, session: Session, video_id: int) -> list[Comment]:
    stmt = (
        select(Comment)
        .where(Comment.video_id == video_id)
        .order_by(Comment.created_at.asc())
    )
    return session.exec(stmt).all()


def delete_user_comment(
    *,
    session: Session,
    comment_id: int,
    user_id: int,
) -> bool:
    comment = session.get(Comment, comment_id)
    if not comment or comment.user_id != user_id:
        return False

    # orphan children
    session.exec(
        update(Comment)
        .where(Comment.parent_comment_id == comment_id)
        .values(parent_comment_id=None)
    )

    session.delete(comment)

    session.exec(
        update(Video)
        .where(Video.id == comment.video_id, Video.comments_count > 0)
        .values(comments_count=Video.comments_count - 1)
    )

    session.commit()
    return True

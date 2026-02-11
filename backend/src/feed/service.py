from sqlmodel import Session, select
from sqlalchemy import func, case

from src.feed.schema import FeedSchema, FeedItemSchema
from src.user_interactions.models import Like
from src.videos.models import Video
from src.auth.models import User
from src.auth.utils import get_current_user
from src.db import get_session


def get_feed_videos(
    *,
    session: Session,
    current_user,
    limit: int = 20,
    offset: int = 0,
) -> FeedSchema:

    liked_subq = (
        select(Like.video_id)
        .where(Like.user_id == current_user.id)
        .subquery()
    )

    stmt = (
        select(
            Video.id.label("video_id"),
            Video.caption,
            Video.processed_path.label("video_url"),
            Video.thumbnail_path.label("thumbnail_url"),
            Video.likes_count,
            Video.comments_count,
            Video.created_at,
            User.username.label("owner_username"),
            User.profile_pic.label("owner_profile_pic"),
            case(
                (liked_subq.c.video_id.isnot(None), True),
                else_=False,
            ).label("is_liked_by_user"),
        )
        .join(User, User.id == Video.user_id)
        # Uncomment when follow-based feed is enabled
        # .join(Follow, Follow.followed_id == Video.user_id)
        # .where(Follow.follower_id == current_user.id)
        .outerjoin(liked_subq, liked_subq.c.video_id == Video.id)
        .where(Video.status == "READY")
        .order_by(Video.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    rows = session.exec(stmt).all()

    items = [
        FeedItemSchema(
            video_id=row.video_id,
            owner_username=row.owner_username,
            owner_profile_pic=row.owner_profile_pic,
            caption=row.caption,
            video_url=row.video_url,
            thumbnail_url=row.thumbnail_url,
            likes_count=row.likes_count,
            comments_count=row.comments_count,
            is_liked_by_user=row.is_liked_by_user,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return FeedSchema(items=items)

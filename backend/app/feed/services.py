from sqlalchemy.orm import joinedload

from app.videos.models import Video
from app.auth.models import User
from app.users.models import Follow
from app.feed.schema import FeedItemSchema, FeedSchema


def _map_video_to_feed_item(video: Video, db) -> FeedItemSchema:
    '''
    Docstring for _map_video_to_feed_item
    
    :param video: Description
    :type video: Video
    :return: Description
    :rtype: FeedItemSchema
    '''
    # get user for video owner info
    owner = db.query(User).filter(User.id == video.owner_id).first()

    feed_item = FeedItemSchema(
        video_id=video.id,
        owner_username=owner.username if owner else None,
        owner_profile_pic=owner.profile_pic if owner else None,
        caption=video.caption,
        video_url=video.video_url,
        thumbnail_url=video.thumbnail_url,
        likes_count=video.likes_count or 0,
        comments_count=video.comments_count or 0,
        created_at=video.created_at.isoformat() if video.created_at else None,
    )
    return feed_item

def get_feed_videos(current_user: User, db, limit: int = 10, offset: int = 0) -> list[Video]:
    '''
    Docstring for get_feed_videos
    
    :param db: Description
    :param limit: Description
    :type limit: int
    :param offset: Description
    :type offset: int
    :return: Description
    :rtype: list[Video]

    SELECT videos.*
    FROM videos
    JOIN follows
    ON videos.owner_id = follows.followed_id
    WHERE follows.follower_id = :current_user_id
    AND videos.status = 'PUBLISHED'
    ORDER BY videos.created_at DESC
    LIMIT 20;   
    '''

    # videos = (
    #     db.query(Video)
    #     .join(Follow, Video.owner_id == Follow.followed_id)
    #     .filter(Follow.follower_id == current_user.id)
    #     .filter(Video.status == 'PUBLISHED')
    #     .order_by(Video.created_at.desc())
    #     .limit(limit)
    #     .offset(offset)
    # )

    # if videos is None:
    #     # return all videos if no followed users have published videos
    #     videos = (
    #         db.query(Video)
    #         .filter(Video.status == 'PUBLISHED')
    #         .order_by(Video.created_at.desc())
    #         .limit(limit)
    #         .offset(offset)
    #     )

    #     feed = FeedSchema(items=[])
    #     for video in videos:
    #         feedItem = _map_video_to_feed_item(video, db)
    #         feed.items.append(feedItem)
    #     return feed

    # feed = FeedSchema(items=[])

    # for video in videos:
    #     feedItem = _map_video_to_feed_item(video, db)
    #     feed.items.append(feedItem)

    # return all videos on the platform as feed for now
    videos = (
        db.query(Video)
        .filter(Video.status == 'PUBLISHED')
        .order_by(Video.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    feed = FeedSchema(items=[])
    for video in videos:
        feedItem = _map_video_to_feed_item(video, db)
        feed.items.append(feedItem)

    return feed

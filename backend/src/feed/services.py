from src.videos.models import Video
from src.auth.models import User
from src.feed.schema import FeedItemSchema, FeedSchema
from src.user_interactions.models import Like


def _map_video_to_feed_item(video: Video, db, is_liked_by_user: bool = False) -> FeedItemSchema:
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
        is_liked_by_user=is_liked_by_user,
        created_at=video.created_at.isoformat() if video.created_at else None,
    )
    return feed_item

def _fetch_likes_of_current_user(current_user: User, video_ids: list[int], db) -> set[int]:
    if not video_ids:
        return set()
    return {
        row[0]
        for row in db.query(Like.video_id)
        .filter(Like.user_id == current_user.id, Like.video_id.in_(video_ids))
        .all()
    }

def get_feed_videos(current_user: User, db, limit: int = 10, offset: int = 0) -> list[Video]:
    '''

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
    videos_query = (
        db.query(Video)
        .filter(Video.status == 'PUBLISHED')
        .order_by(Video.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    video_list = videos_query.all()
    feed = FeedSchema(items=[])
    liked_video_ids = _fetch_likes_of_current_user(current_user, [video.id for video in video_list], db)
    for video in video_list:
        is_liked_by_user = video.id in liked_video_ids
        feedItem = _map_video_to_feed_item(video, db, is_liked_by_user=is_liked_by_user)
        feed.items.append(feedItem)

    return feed

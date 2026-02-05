from sqlalchemy import Integer
from sqlalchemy.orm import Session
from app.user_interactions.models import Like, Comment
from app.videos.models import Video


def like(db: Session, user_id: int, video_id: int) -> Like:

    existing_like = db.query(Like).filter(Like.user_id == user_id, Like.video_id == video_id).first()
    if existing_like:
        return None  # User has already liked this video

    like = Like(user_id=user_id, video_id=video_id)

    db.add(like)
    
    # Increment likes_count on the Video
    video = db.query(Video).filter(Video.id == video_id).first()
    if video:
        video.likes_count += 1
    
    db.commit()
    db.refresh(like)
    return like


def unlike(db: Session, user_id: int, video_id: int) -> bool:
    like = db.query(Like).filter(Like.user_id == user_id, Like.video_id == video_id).first()
    if like:
        db.delete(like)
        
        # Decrement likes_count on the Video
        video = db.query(Video).filter(Video.id == video_id).first()
        if video and video.likes_count > 0:
            video.likes_count -= 1
        
        db.commit()
        return True
    return False


def comment_on_video(db: Session, user_id: int, video_id: int, content: str, parent_comment_id: int = None) -> Comment:
    comment = Comment(
        user_id=user_id,
        video_id=video_id,
        content=content,
        parent_comment_id=parent_comment_id,
    )
    db.add(comment)
    
    # Increment comments_count on the Video
    video = db.query(Video).filter(Video.id == video_id).first()
    if video:
        video.comments_count += 1
    
    db.commit()
    db.refresh(comment)
    return comment


def get_comments_data(db: Session, video_id: int) -> list[Comment]:
    comments = db.query(Comment).filter(Comment.video_id == video_id).order_by(Comment.created_at.asc()).all()
    return comments


def delete_user_comment(db: Session, comment_id: int, user_id: int) -> bool:
    # allow comment delete if the comment belongs to the user
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == user_id).first()
    if comment:
        video_id = comment.video_id
        db.delete(comment)

        # set child comments' parent_comment_id to None
        child_comments = db.query(Comment).filter(Comment.parent_comment_id == comment_id).all()
        for child in child_comments:
            child.parent_comment_id = None
        
        # Decrement comments_count on the Video
        video = db.query(Video).filter(Video.id == video_id).first()
        if video and video.comments_count > 0:
            video.comments_count -= 1
        
        db.commit()
        return True
    return False
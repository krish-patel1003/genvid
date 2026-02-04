from app.videos.models import Video
from app.auth.models import User


def create_video_record(db, owner_id: int, caption: str = None) -> Video:
    new_video = Video(
        owner_id=owner_id,
        caption=caption,
        status="DRAFT",
        created_at="2024-01-01T00:00:00Z"  # Placeholder timestamp
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    return new_video

def get_video_by_id(db, video_id: int) -> Video:
    return db.query(Video).filter(Video.id == video_id).first()

def delete_video_record(db, video: Video):
    db.delete(video)
    db.commit()
    return

def get_videos_by_owner(db, owner: User) -> list[Video]:
    return db.query(Video).filter(Video.owner_id == owner.id).all()
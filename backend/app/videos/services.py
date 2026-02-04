from app.videos.models import Video
from app.auth.models import User

def get_video_by_id(db, video_id: int) -> Video:
    return db.query(Video).filter(Video.id == video_id).first()

def delete_video_record(db, video: Video):
    db.delete(video)
    db.commit()
    return

def get_videos_by_owner(db, owner: User) -> list[Video]:
    return db.query(Video).filter(Video.owner_id == owner.id).all()
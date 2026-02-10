from sqlmodel import Session, select

from src.videos.models import Video
from src.videos.schema import VideoCreate
from src.auth.models import User


def create_video(data: VideoCreate, user: User, session: Session) -> Video:
    video = Video(
        title=data.title,
        description=data.description,
        user_id=user.id,
    )
    session.add(video)
    session.commit()
    session.refresh(video)

    return video


def list_user_videos(user: User, session: Session) -> list[Video]:
    videos = session.exec(
        select(Video).where(Video.user_id == user.id)
    ).all()
    return videos

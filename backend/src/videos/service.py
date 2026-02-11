from sqlmodel import Session, select

from src.videos.models import Video, VideoGenerationJob
from src.videos.schema import GenerationCreate, VideoCreate, VideoObject, VideosResponse
from src.videos.enums import GenerationStatus
from src.auth.models import User
from src.gcp.publisher import publish_generation_job


def create_video(data: VideoCreate, user: User, session: Session) -> Video:
    video = Video(
        caption=data.caption,
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

    # convert to VideoObject schema
    videos = [VideoObject.model_validate(v) for v in videos]
    return VideosResponse(videos=videos)


def create_generation_task(
    data: GenerationCreate,
    session: Session,
    user: User,
) -> VideoGenerationJob:
    
    job = VideoGenerationJob(
        user_id=user.id,
        prompt=data.prompt,
        status=GenerationStatus.QUEUED,
    )

    session.add(job)
    session.commit()
    session.refresh(job)

    publish_generation_job(job.id)

    return job

from fastapi import APIRouter, Depends, Request, HTTPException

from app.core.dependencies import get_db, get_current_user
from app.videos.schemas import VideoUploadSchema, VideoPublicSchema, VideoGenerationCreateSchema, VideoGenerationObjectSchema
from app.videos.services import get_video_by_id, delete_video_record, get_videos_by_owner
from app.videos.models import Video, VideoGenerationObject
from workers.video_generation.tasks import generate_video_task
from app.videos.enums import VideoStatusEnum

router = APIRouter(prefix="/videos", tags=["videos"])

@router.post("/create", response_model=VideoGenerationObjectSchema)
def create_video_generation_request(
    data: VideoGenerationCreateSchema,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    video_gen_obj = VideoGenerationObject(
        prompt=data.prompt,
        status=VideoStatusEnum.DRAFT,
    )
    
    db.add(video_gen_obj)
    db.commit()
    db.refresh(video_gen_obj)

    # Trigger the Celery task to generate the video asynchronously
    generate_video_task.delay(video_gen_obj.id)

    return video_gen_obj



@router.post("/generation/{generation_id}/publish", response_model=VideoPublicSchema)
def publish_generated_video(
    generation_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    video_gen_obj = db.query(VideoGenerationObject).get(generation_id)
    if not video_gen_obj:
        raise HTTPException(status_code=404, detail="VideoGenerationObject not found")
    if video_gen_obj.status != VideoStatusEnum.READY:
        raise HTTPException(status_code=400, detail="Video is not ready for publishing")

    # video_url = upload_to_cloud_storage(video_gen_obj.file_path)  # Placeholder for actual upload logic
    video_url = f"https://cloudstorage.example.com/{video_gen_obj.file_path.split('/')[-1]}" # Dummy URL

    # Create Video record
    video = Video(
        owner_id=current_user.id,
        caption="Generated Video",
        video_url=video_url,
        status=VideoStatusEnum.PUBLISHED,
    )

    db.add(video)
    db.commit()
    db.refresh(video)

    return video


@router.get("/{video_id}", response_model=VideoPublicSchema)
def get_video(
    video_id: int,
    db=Depends(get_db),
):
    
    video = get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.delete("/{video_id}", status_code=204)
def delete_video(
    video_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    video = get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this video")

    delete_video_record(db, video)
    return

@router.get("/user/videos", response_model=list[VideoPublicSchema])
def get_user_videos(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    videos = get_videos_by_owner(db, current_user)
    return videos
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json
import time
from sqlmodel import Session, select

from src.db import get_session
from src.auth.utils import get_current_user
from src.videos.models import VideoGenerationJob

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/video-generation")
def stream_events(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    def event_stream():
        while True:
            stmt = (
                select(VideoGenerationJob)
                .where(VideoGenerationJob.user_id == current_user.id)
                .order_by(VideoGenerationJob.created_at.desc())
            )
            jobs = session.exec(stmt).all()

            yield f"data: {json.dumps([{'id': j.id, 'status': j.status, 'preview': j.preview_video_path} for j in jobs])}\n\n"

            time.sleep(3)

    return StreamingResponse(event_stream(), media_type="text/event-stream")

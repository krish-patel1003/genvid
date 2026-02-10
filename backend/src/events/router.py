
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import time
import json
from sqlmodel import Session, select

from src.db import get_session
from src.auth.utils import get_current_user
from src.videos.models import VideoGenerationJob
from src.auth.models import User

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def event_stream(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    def stream():
        last_seen = None
        while True:
            stmt = (
                select(VideoGenerationJob)
                .where(VideoGenerationJob.user_id == user.id)
                .order_by(VideoGenerationJob.updated_at.desc())
            )
            jobs = session.exec(stmt).all()

            payload = [
                {
                    "id": j.id,
                    "status": j.status,
                    "preview": j.preview_video_path,
                }
                for j in jobs
            ]

            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(3)

    return StreamingResponse(stream(), media_type="text/event-stream")

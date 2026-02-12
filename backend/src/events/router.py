from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json
import time
from sqlmodel import Session, select

from src.db import get_session
from src.auth.utils import get_current_user
from src.videos.models import VideoGenerationJob
from src.security import decode_token
from src.db import engine
import asyncio
from fastapi import Query


router = APIRouter(prefix="/events", tags=["events"])

@router.get("/video-generation")
async def video_generation_events(token: str = Query(...)):

    payload = decode_token(token)
    user_id = int(payload["sub"])

    async def event_stream():
        last_payload = None

        while True:
            try:
                with Session(engine) as session:
                    jobs = session.exec(
                        select(VideoGenerationJob)
                        .where(VideoGenerationJob.user_id == user_id)
                        .order_by(VideoGenerationJob.updated_at.desc())
                    ).all()

                data = [
                    {
                        "id": j.id,
                        "status": j.status,
                        "prompt": j.prompt,
                        "preview_video_path": j.preview_video_path,
                        "preview_thumbnail_path": j.preview_thumbnail_path,
                        "error_message": j.error_message,
                        "published_video_id": j.published_video_id,
                        "updated_at": j.updated_at.isoformat() if j.updated_at else None,
                    }
                    for j in jobs
                ]

                payload_json = json.dumps(data)

                if payload_json != last_payload:
                    last_payload = payload_json
                    yield f"data: {payload_json}\n\n"
                else:
                    # heartbeat
                    yield f": ping {int(time.time())}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

            await asyncio.sleep(3)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

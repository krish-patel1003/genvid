# worker/dummy_video_worker.py

import time
from sqlmodel import Session
from src.db import engine
from src.videos.models import VideoGenerationJob
from src.videos.enums import GenerationStatus

def run(job_id: int):
    with Session(engine) as session:
        job = session.get(VideoGenerationJob, job_id)
        if not job:
            return

        job.status = GenerationStatus.RUNNING
        session.add(job)
        session.commit()

        # simulate work
        time.sleep(10)

        job.preview_video_path = f"gs://genvid/previews/{job_id}.mp4"
        job.preview_thumbnail_path = f"gs://genvid/previews/{job_id}.jpg"
        job.status = GenerationStatus.SUCCEEDED

        session.add(job)
        session.commit()

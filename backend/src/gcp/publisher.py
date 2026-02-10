
from google.cloud import pubsub_v1
import json
from src.config import get_settings

settings = get_settings()
PROJECT_ID = settings.GCP_PROJECT_ID
TOPIC = settings.GCP_PUBSUB_VIDEO_GEN_TOPIC

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC)


def publish_generation_job(job_id: int):
    publisher.publish(
        topic_path,
        json.dumps({"job_id": job_id}).encode("utf-8"),
    )

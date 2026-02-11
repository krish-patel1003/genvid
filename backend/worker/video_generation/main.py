import os
import json
import time
import logging
import tempfile
import psycopg2
from google import genai
from google.genai import types
from google.cloud import storage
import argparse

logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.environ["DATABASE_URL"]
GCS_BUCKET = os.environ["GCS_BUCKET"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]


# ---------------------------
# DB Utilities
# ---------------------------

def get_conn():
    return psycopg2.connect(DATABASE_URL)


def mark_running(conn, job_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE video_generation_jobs
            SET status='RUNNING',
                updated_at=NOW()
            WHERE id=%s
            """,
            (job_id,),
        )
    conn.commit()


def mark_success(conn, job_id, preview_path):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE video_generation_jobs
            SET status='SUCCEEDED',
                preview_video_path=%s,
                updated_at=NOW()
            WHERE id=%s
            """,
            (preview_path, job_id),
        )
    conn.commit()


def mark_failed(conn, job_id, error_message):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE video_generation_jobs
            SET status='FAILED',
                error_message=%s,
                updated_at=NOW()
            WHERE id=%s
            """,
            (error_message[:500], job_id),
        )
    conn.commit()


# ---------------------------
# Veo Generation
# ---------------------------

def generate_with_veo(prompt: str, duration_seconds: int = 4) -> str:
    logging.info("Starting Veo generation")

    client = genai.Client(api_key=GOOGLE_API_KEY)

    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",  # mobile vertical
            resolution="720p",
            duration_seconds=duration_seconds,
            person_generation="allow_all",
        ),
    )

    while not operation.done:
        logging.info("Waiting for Veo...")
        time.sleep(8)
        operation = client.operations.get(operation)

    if operation.error:
        raise RuntimeError(f"Veo failed: {operation.error}")

    if not operation.response or not operation.response.generated_videos:
        raise RuntimeError("Veo returned empty response")

    generated_video = operation.response.generated_videos[0]

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        client.files.download(file=generated_video.video)
        generated_video.video.save(tmp.name)
        return tmp.name


# ---------------------------
# Upload to GCS
# ---------------------------

def upload_to_gcs(job_id: int, local_path: str) -> str:
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)

    object_name = f"previews/{job_id}/preview_{int(time.time())}.mp4"

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_path, content_type="video/mp4")

    logging.info(f"Uploaded preview to {object_name}")

    return object_name


# ---------------------------
# Main Entry
# ---------------------------

def main():
    # 1. Setup the parser
    parser = argparse.ArgumentParser(description="Cloud Run Job Worker")

    # 2. Define your expected arguments
    # argparse handles the "--key=value" or "--key value" format automatically
    parser.add_argument("--job_id", type=int, help="The ID of the job")
    parser.add_argument("--prompt", type=str, help="The text prompt for generation")

    # 3. Parse the arguments from sys.argv
    args, unknown = parser.parse_known_args()

    logging.info(f"Received job_id: {args.job_id}")
    logging.info(f"Received prompt: {args.prompt}")

    job_id = args.job_id
    prompt = args.prompt

    conn = get_conn()

    try:
        logging.info(f"Processing job {job_id}")

        mark_running(conn, job_id)

        local_clip = generate_with_veo(prompt, duration_seconds=4)

        preview_path = upload_to_gcs(job_id, local_clip)

        mark_success(conn, job_id, preview_path)

        logging.info(f"Job {job_id} completed")

    except Exception as e:
        logging.exception("Generation failed")
        mark_failed(conn, job_id, str(e))

    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    main()

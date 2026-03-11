import os
import json
import time
import logging
import tempfile
from pathlib import Path
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


def fetch_job_input(conn, job_id: int) -> tuple[str, list[str]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT prompt, reference_image_paths
            FROM video_generation_jobs
            WHERE id=%s
            """,
            (job_id,),
        )
        row = cur.fetchone()

    if not row:
        raise RuntimeError(f"Job not found: {job_id}")

    prompt, reference_image_paths = row
    if reference_image_paths is None:
        reference_image_paths = []
    elif isinstance(reference_image_paths, str):
        reference_image_paths = json.loads(reference_image_paths)

    return prompt, list(reference_image_paths)


# ---------------------------
# Veo Generation
# ---------------------------

def _build_reference_images(reference_local_files: list[str] | None):
    if not reference_local_files:
        return None

    references = []
    for local_path in reference_local_files:
        image = types.Image.from_file(location=local_path)
        references.append(
            types.VideoGenerationReferenceImage(
                image=image,
                reference_type=types.VideoGenerationReferenceType.ASSET,
            )
        )
    return references


def generate_with_veo(
    prompt: str,
    duration_seconds: int = 4,
    reference_local_files: list[str] | None = None,
) -> str:
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
            reference_images=_build_reference_images(reference_local_files),
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


def download_reference_images(reference_image_paths: list[str]) -> list[str]:
    if not reference_image_paths:
        return []

    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    local_paths: list[str] = []

    for object_name in reference_image_paths:
        normalized = object_name
        if object_name.startswith("gs://"):
            trimmed = object_name[5:]
            bucket_name, _, normalized_object = trimmed.partition("/")
            if bucket_name and bucket_name != GCS_BUCKET:
                raise RuntimeError(
                    f"Reference image bucket mismatch: expected {GCS_BUCKET}, got {bucket_name}"
                )
            normalized = normalized_object

        suffix = Path(normalized).suffix or ".jpg"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            local_path = tmp.name

        blob = bucket.blob(normalized)
        blob.download_to_filename(local_path)
        local_paths.append(local_path)

    return local_paths


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
    if not job_id:
        raise RuntimeError("Missing required --job_id")

    conn = get_conn()
    local_reference_files: list[str] = []
    local_clip: str | None = None

    try:
        logging.info(f"Processing job {job_id}")

        mark_running(conn, job_id)

        prompt_from_db, reference_image_paths = fetch_job_input(conn, job_id)
        prompt = args.prompt or prompt_from_db
        if not prompt:
            raise RuntimeError("Prompt is missing for job")

        local_reference_files = download_reference_images(reference_image_paths)

        local_clip = generate_with_veo(
            prompt,
            duration_seconds=4,
            reference_local_files=local_reference_files,
        )

        preview_path = upload_to_gcs(job_id, local_clip)

        mark_success(conn, job_id, preview_path)

        logging.info(f"Job {job_id} completed")

    except Exception as e:
        logging.exception("Generation failed")
        mark_failed(conn, job_id, str(e))

    finally:
        if local_clip:
            try:
                os.remove(local_clip)
            except OSError:
                pass
        for path in local_reference_files:
            try:
                os.remove(path)
            except OSError:
                pass
        conn.close()


if __name__ == "__main__":
    import sys
    main()

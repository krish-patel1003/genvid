import base64
import json
import os
import time
import logging
import traceback
import psycopg2
import numpy as np


logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.environ["DATABASE_URL"]

# TODO: add idempotency guard (check status == QUEUED)
# TODO: add retry-safe logic
# TODO: move generation to GPU Cloud Run Job
# TODO: upload preview to GCS instead of dummy path
def update_job_status(job_id, status, preview_path=None, error_message=None):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    try:
        if preview_path:
            cur.execute(
                """
                UPDATE video_generation_jobs
                SET status=%s,
                    preview_video_path=%s,
                    updated_at=NOW()
                WHERE id=%s
                """,
                (status, preview_path, job_id),
            )
        elif error_message:
            cur.execute(
                """
                UPDATE video_generation_jobs
                SET status=%s,
                    error_message=%s,
                    updated_at=NOW()
                WHERE id=%s
                """,
                (status, error_message, job_id),
            )
        else:
            cur.execute(
                """
                UPDATE video_generation_jobs
                SET status=%s,
                    updated_at=NOW()
                WHERE id=%s
                """,
                (status, job_id),
            )

        conn.commit()

    except Exception as e:
        logging.error(f"Failed to update job {job_id}: {str(e)}")
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


def dummy_generate(prompt):
    logging.info(f"Starting dummy generation for prompt: {prompt}")

    time.sleep(5)

    frames = []
    for i in range(24):
        frame = np.zeros((256, 256, 3))
        frame[:, :, 0] = i / 24
        frames.append(frame)

    logging.info("Dummy generation completed")

    return "/dummy/previews/generated.mp4"


def handle_pubsub(event, context):
    try:
        data = base64.b64decode(event["data"]).decode("utf-8")
        payload = json.loads(data)

        job_id = payload["job_id"]
        prompt = payload["prompt"]

        logging.info(f"Received job {job_id}")

        # mark RUNNING
        update_job_status(job_id, "RUNNING")

        preview_path = dummy_generate(prompt)

        update_job_status(job_id, "SUCCEEDED", preview_path=preview_path)

        logging.info(f"Job {job_id} succeeded")

    except Exception as e:
        error_message = str(e)
        logging.error(f"Job failed: {error_message}")
        logging.error(traceback.format_exc())

        try:
            update_job_status(job_id, "FAILED", error_message=error_message)
        except Exception as db_error:
            logging.error(f"Failed to persist error: {str(db_error)}")

import base64
import json
import os
import logging
import traceback
import psycopg2
from google.cloud import run_v2

logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.environ["DATABASE_URL"]
PROJECT_ID = os.environ.get("PROJECT_ID", "genvidgcp")
REGION = os.environ["REGION"]
GPU_JOB_NAME = os.environ["GPU_JOB_NAME"]


def update_job_status(job_id, status, error_message=None):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    try:
        if error_message:
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
        logging.error(f"DB update failed for job {job_id}: {str(e)}")
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


def trigger_gpu_job(payload: dict):
    client = run_v2.JobsClient()

    job_path = client.job_path(PROJECT_ID, REGION, GPU_JOB_NAME)

    logging.info(f"Triggering Cloud Run Job: {GPU_JOB_NAME}")

    request = run_v2.RunJobRequest(
        name=job_path,
        overrides=run_v2.RunJobRequest.Overrides(
            container_overrides=[
                run_v2.RunJobRequest.Overrides.ContainerOverride(
                    args=[
                        "--job_id", str(payload["job_id"]),
                        "--prompt", payload["prompt"],
                    ]
                )
            ]
        ),
    )

    client.run_job(request=request)


def handle_pubsub(event, context):
    try:
        data = base64.b64decode(event["data"]).decode("utf-8")
        payload = json.loads(data)

        job_id = payload["job_id"]

        logging.info(f"Dispatching job {job_id}")

        # Mark RUNNING before triggering
        update_job_status(job_id, "RUNNING")

        trigger_gpu_job(payload)

        logging.info(f"GPU job dispatched for {job_id}")

    except Exception as e:
        logging.error(traceback.format_exc())
        try:
            update_job_status(payload.get("job_id"), "FAILED", error_message=str(e))
        except Exception:
            logging.error("Failed to mark job as FAILED")

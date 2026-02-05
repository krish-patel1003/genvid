from datetime import timedelta
from google.cloud import storage

def generate_signed_url(client: storage.Client, blob_name: str) -> str:
    bucket = client.bucket("genvid_videos_dev_v1")
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=1),
        method="GET",
    )

    return url

def get_gcs_client():
    from google.cloud import storage
    return storage.Client()


def generate_presigned_url(bucket_name: str, blob_name: str, expiration: int = 3600) -> str:
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=expiration,
        method="PUT",
        content_type="application/octet-stream",
    )
    return url


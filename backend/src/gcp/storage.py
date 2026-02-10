import datetime
from google.cloud import storage

def signed_get_url(bucket_name: str, object_name: str, minutes=30) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    return blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=minutes),
        method="GET",
    )


def signed_put_url(bucket_name: str, object_name: str, content_type: str, minutes=15) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    return blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=minutes),
        method="PUT",
        content_type=content_type,
    )

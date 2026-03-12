import google.auth
from google.auth.transport import requests
from google.auth import compute_engine
from datetime import datetime, timedelta
from google.cloud import storage
from fastapi import UploadFile


def signed_get_url(bucket_name: str, object_name: str, minutes: int = 30):
    # Get default credentials (Cloud Run service account)
    auth_request = requests.Request()
    credentials, project = google.auth.default()

    # Create storage client
    storage_client = storage.Client(project=project, credentials=credentials)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    # This is the important trick:
    # Use IDTokenCredentials to enable IAM-based signing
    signing_credentials = compute_engine.IDTokenCredentials(
        auth_request,
        "",
        service_account_email='286573941342-compute@developer.gserviceaccount.com',
    )

    signed_url = blob.generate_signed_url(
        expiration=datetime.utcnow() + timedelta(minutes=minutes),
        version="v4",
        credentials=signing_credentials,
    )

    return signed_url


def upload_upload_file_to_bucket(
    *,
    bucket_name: str,
    destination_blob_name: str,
    file: UploadFile,
) -> str:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    file.file.seek(0)
    blob.upload_from_file(file.file, content_type=file.content_type)
    return destination_blob_name


def delete_object(bucket_name: str, object_name: str) -> None:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.delete()

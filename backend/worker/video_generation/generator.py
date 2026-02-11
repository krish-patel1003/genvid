# import os
# import time
# import tempfile
# import logging
# import imageio
# from google.cloud import storage

# from damo_text_to_video import DamoTextToVideoGenerator

# logging.basicConfig(level=logging.INFO)

# GCS_BUCKET = os.environ["GCS_BUCKET"]


# def generate_video(job_id: int, prompt: str) -> str:
#     logging.info(f"Generating preview for job {job_id}")

#     generator = DamoTextToVideoGenerator()
#     generator.load()

#     frames = generator.generate(prompt)
#     uint8_frames = generator.to_uint8(frames)

#     # Save locally first
#     with tempfile.TemporaryDirectory() as tmpdir:
#         local_path = os.path.join(tmpdir, "preview.mp4")

#         logging.info("Encoding video to MP4")
#         imageio.mimsave(
#             local_path,
#             uint8_frames,
#             fps=8,
#             quality=8,
#         )

#         # Upload to GCS
#         client = storage.Client()
#         bucket = client.bucket(GCS_BUCKET)

#         object_name = f"previews/{job_id}/preview_{int(time.time())}.mp4"

#         blob = bucket.blob(object_name)

#         logging.info(f"Uploading preview to GCS: {object_name}")
#         blob.upload_from_filename(local_path, content_type="video/mp4")

#     logging.info("Upload completed")

#     return object_name

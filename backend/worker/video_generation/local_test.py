import os
import time
import tempfile
import imageio
from google import genai
from google.genai import types


# Use env variable for API key
API_KEY = os.environ["GOOGLE_API_KEY"]


def generate_4s_video(prompt: str) -> str:
    client = genai.Client(api_key=API_KEY)

    print("Starting Veo request...")

    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",
            resolution="720p",
            duration_seconds=4,
            person_generation="allow_all",
        ),
    )

    while not operation.done:
        print("Waiting for Veo...")
        time.sleep(8)
        operation = client.operations.get(operation)
    
    print(type(operation))
    print(operation.__dict__)

    if operation.error:
        raise RuntimeError(f"Veo failed: {operation.error}")

    if not operation.response or not operation.response.generated_videos:
        raise RuntimeError("Veo returned empty response")

    generated_video = operation.response.generated_videos[0]

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        client.files.download(file=generated_video.video)
        generated_video.video.save(tmp.name)
        print("Saved 4s clip to:", tmp.name)
        return tmp.name


import subprocess

def expand_to_30_seconds(input_path: str, output_path: str):
    """
    Repeat input video to approx 30 seconds using ffmpeg
    """

    command = [
        "ffmpeg",
        "-stream_loop", "7",  # repeat 7 times (4s * 8 ≈ 32s)
        "-i", input_path,
        "-c", "copy",         # no re-encode (fast)
        "-t", "30",           # trim to 30 seconds
        output_path,
        "-y"
    ]

    subprocess.run(command, check=True)

    print("Expanded to 30 seconds:", output_path)



if __name__ == "__main__":
    prompt = """a person walking through a colorful theme park at sunset
"""

    short_path = generate_4s_video(prompt)

    final_path = "local_30s_preview.mp4"
    expand_to_30_seconds(short_path, final_path)

import time
from pathlib import Path

OUTPUT_DIR = Path("generated_videos")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_video(prompt: str, video_id: int) -> str:
    """
    Dummy generator for now.
    Later this is where ML goes.
    """
    print(f"Generating video for prompt: {prompt}")
    
    time.sleep(5)  # simulate heavy work

    output_path = OUTPUT_DIR / f"{video_id}.mp4"

    # fake video file
    with open(output_path, "wb") as f:
        f.write(b"FAKE VIDEO CONTENT")

    return str(output_path)
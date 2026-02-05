import time
import shutil
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
print("BASE DIR:", BASE_DIR)
STOCK_VIDEO = BASE_DIR / "stock_videos" / "demo_vid.mp4"
OUTPUT_DIR = BASE_DIR / "generated_videos"

OUTPUT_DIR.mkdir(exist_ok=True)


def generate_video(prompt: str, video_id: int) -> str:
    """
    Temporary generator:
    Copies a demo video so frontend can play it.
    """
    print(f"Generating video for prompt: {prompt}")

    # simulate generation time
    time.sleep(5)

    output_path = OUTPUT_DIR / f"{video_id}.mp4"

    if not STOCK_VIDEO.exists():
        raise FileNotFoundError(f"Stock video not found at {STOCK_VIDEO}")

    shutil.copyfile(STOCK_VIDEO, output_path)

    print("Source size:", os.path.getsize(STOCK_VIDEO))
    print("Output size:", os.path.getsize(output_path))

    return str(output_path)

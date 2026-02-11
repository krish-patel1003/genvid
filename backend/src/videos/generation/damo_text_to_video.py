import time
from typing import List

import torch
import numpy as np
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler

from src.videos.generation.base import VideoGenerator   


class DamoTextToVideoGenerator(VideoGenerator):
    def __init__(
        self,
        model_id: str = "damo-vilab/text-to-video-ms-1.7b",
        device: str = "cuda",
        torch_dtype=torch.float16,
        steps: int = 25,
        frames_per_clip: int = 24,
        repeat: int = 1,
    ):
        self.model_id = model_id
        self.device = device
        self.torch_dtype = torch_dtype
        self.steps = steps
        self.frames_per_clip = frames_per_clip
        self.repeat = repeat

        self.pipe = None

    # ---------------------------------------------------
    # Load model once (heavy operation)
    # ---------------------------------------------------
    def load(self) -> None:
        t0 = time.time()

        self.pipe = DiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=self.torch_dtype,
            variant="fp16" if self.torch_dtype == torch.float16 else None,
        ).to(self.device)

        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )

        t1 = time.time()
        print(f"[Generator] Model loaded in {t1 - t0:.2f}s")

    # ---------------------------------------------------
    # Generate frames (float32 [0,1])
    # ---------------------------------------------------
    def generate(self, prompt: str) -> List[np.ndarray]:
        if self.pipe is None:
            raise RuntimeError("Generator not loaded. Call load() first.")

        t0 = time.time()

        result = self.pipe(
            prompt,
            num_inference_steps=self.steps,
            num_frames=self.frames_per_clip,
        )

        clip_frames = result.frames[0]

        processed_frames: List[np.ndarray] = []

        for frame in clip_frames:
            if hasattr(frame, "cpu"):
                frame = frame.cpu().numpy()

            # Convert CHW → HWC if needed
            if frame.ndim == 3 and frame.shape[0] in (1, 3, 4):
                frame = np.transpose(frame, (1, 2, 0))

            # Ensure float32 in [0,1]
            frame = frame.astype(np.float32)
            frame = np.clip(frame, 0.0, 1.0)

            # Drop alpha channel if present
            if frame.shape[-1] == 4:
                frame = frame[:, :, :3]

            processed_frames.append(frame)

        # Repeat if needed (e.g., 3s clip × 10 = 30s)
        if self.repeat > 1:
            processed_frames = processed_frames * self.repeat

        t1 = time.time()
        print(f"[Generator] Generation completed in {t1 - t0:.2f}s")

        return processed_frames

    # ---------------------------------------------------
    # Optional: Convert to uint8 for encoding
    # ---------------------------------------------------
    @staticmethod
    def to_uint8(frames: List[np.ndarray]) -> List[np.ndarray]:
        uint8_frames = []
        for frame in frames:
            f = (frame * 255).clip(0, 255).astype(np.uint8)
            uint8_frames.append(f)
        return uint8_frames


class DummyVideoGenerator(VideoGenerator):
    def load(self) -> None:
        pass

    def generate(self, prompt: str) -> List[np.ndarray]:
        return [
            np.random.rand(512, 512, 3).astype(np.float32) for _ in range(24)
        ]
    
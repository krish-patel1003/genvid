import torch
import numpy as np
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler

from src.videos.generation.base import VideoGenerator


class DamoTextToVideo(VideoGenerator):
    def __init__(
        self,
        model_id: str = "damo-vilab/text-to-video-ms-1.7b",
        steps: int = 25,
        frames: int = 24,
        device: str = "cuda",
    ):
        self.model_id = model_id
        self.steps = steps
        self.frames = frames
        self.device = device
        self.pipe = None

    def load(self) -> None:
        self.pipe = DiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16,
            variant="fp16",
        ).to(self.device)

        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )

    def generate(self, prompt: str):
        result = self.pipe(
            prompt,
            num_inference_steps=self.steps,
            num_frames=self.frames,
        )

        frames = result.frames[0]

        processed = []
        for frame in frames:
            if hasattr(frame, "cpu"):
                frame = frame.cpu().numpy()

            if frame.ndim == 3 and frame.shape[0] in (1, 3, 4):
                frame = np.transpose(frame, (1, 2, 0))

            frame = frame.clip(0, 1)
            processed.append(frame)

        return processed

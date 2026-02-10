from abc import ABC, abstractmethod
from typing import List
import numpy as np
import imageio

class VideoGenerator(ABC):
    @abstractmethod
    def load(self) -> None:
        pass

    @abstractmethod
    def generate(self, prompt: str) -> List[np.ndarray]:
        """
        Returns a list of frames (H, W, C) in float32 [0, 1]
        """
        pass


class FrameProcessor(ABC):
    @abstractmethod
    def process(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        pass

class ToUint8(FrameProcessor):
    def process(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        out = []
        for f in frames:
            f = (f * 255).clip(0, 255).astype("uint8")
            if f.shape[-1] == 4:
                f = f[:, :, :3]
            out.append(f)
        return out


class VideoAssembler(ABC):
    @abstractmethod
    def assemble(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        pass


class LoopAssembler(VideoAssembler):
    def __init__(self, repeat: int):
        self.repeat = repeat

    def assemble(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        return frames * self.repeat


class VideoEncoder:
    def __init__(self, fps: int = 8):
        self.fps = fps

    def encode(self, frames: List[np.ndarray], path: str):
        imageio.mimsave(
            path,
            frames,
            fps=self.fps,
            quality=8,
        )

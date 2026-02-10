from abc import ABC, abstractmethod
from typing import List
import numpy as np


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



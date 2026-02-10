from typing import List

from src.videos.generation.base import VideoGenerator, FrameProcessor, VideoAssembler, VideoEncoder


class VideoGenerationPipeline:
    def __init__(
        self,
        generator: VideoGenerator,
        processors: List[FrameProcessor],
        assembler: VideoAssembler,
        encoder: VideoEncoder,
    ):
        self.generator = generator
        self.processors = processors
        self.assembler = assembler
        self.encoder = encoder

    def run(self, prompt: str, output_path: str):
        frames = self.generator.generate(prompt)

        for p in self.processors:
            frames = p.process(frames)

        frames = self.assembler.assemble(frames)

        self.encoder.encode(frames, output_path)

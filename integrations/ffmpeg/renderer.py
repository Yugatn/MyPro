"""FFmpeg renderer for the Foundation MVP."""
from __future__ import annotations
import subprocess
from pathlib import Path
from core.identity import hash_bytes
from core.montage.flatten import flatten
from core.render.backend import RenderBackend
from core.render.result import RenderResult
from core.render.specification import RenderSpecification
from .filter_graph import build_ffmpeg_command

class FFmpegRenderer(RenderBackend):
    def __init__(self, ffmpeg_binary: str = "ffmpeg"):
        self.ffmpeg_binary = ffmpeg_binary

    def build_command(self, repository, specification: RenderSpecification) -> list[str]:
        if specification.timeline_id not in repository.timelines:
            raise ValueError(f"unknown timeline: {specification.timeline_id}")
        flat = flatten(repository.timelines, specification.timeline_id)
        if flat.audio_layers and specification.audio_policy == "reject":
            raise ValueError("audio layers require an explicit audio policy")
        media_paths = {asset_id: asset.name for asset_id, asset in repository.media_pool.items()}
        return build_ffmpeg_command(flat, specification, media_paths, self.ffmpeg_binary)

    def render(self, repository, specification: RenderSpecification, *, execute: bool = True) -> RenderResult:
        command = self.build_command(repository, specification)
        if not execute:
            return RenderResult(specification.spec_hash, specification.output_path, tuple(command), False)
        process = subprocess.run(command, capture_output=True, text=True, check=False)
        output_hash = None
        output = Path(specification.output_path)
        if process.returncode == 0 and output.is_file():
            output_hash = hash_bytes(output.read_bytes())
        return RenderResult(
            specification_hash=specification.spec_hash,
            output_path=specification.output_path,
            command=tuple(command),
            executed=True,
            return_code=process.returncode,
            output_hash=output_hash,
            stderr=process.stderr,
        )

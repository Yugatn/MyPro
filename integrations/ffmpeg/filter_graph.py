"""FFmpeg filter graph generation for the Foundation MVP."""
from __future__ import annotations
from core.montage.flatten import FlatTimeline
from core.render.specification import RenderSpecification

def _seconds(value) -> str:
    return f"{float(value):.9f}".rstrip("0").rstrip(".")

def build_video_filter(flat: FlatTimeline, specification: RenderSpecification, input_indices: dict[str, int]) -> str:
    duration = flat.duration.to_seconds()
    fps = f"{specification.fps_num}/{specification.fps_den}"
    nodes = [f"color=c=black:s={specification.width}x{specification.height}:r={fps}:d={_seconds(duration)}[base]"]
    current = "base"
    for number, item in enumerate(flat.video_layers):
        source_id = item.layer.source_id
        if not source_id or source_id not in input_indices:
            raise ValueError("video layer references an unknown media input")
        start = item.effective_range.start.to_seconds()
        end = item.effective_range.end.to_seconds()
        prepared = f"v{number}"
        nodes.append(
            f"[{input_indices[source_id]}:v]trim=start=0:end={_seconds(end-start)},"
            f"setpts=PTS-STARTPTS+{_seconds(start)}/TB,"
            f"scale={specification.width}:{specification.height}[{prepared}]"
        )
        output = f"mix{number}"
        nodes.append(
            f"[{current}][{prepared}]overlay=eof_action=pass:shortest=0:"
            f"enable='between(t,{_seconds(start)},{_seconds(end)})'[{output}]"
        )
        current = output
    nodes.append(f"[{current}]format={specification.pixel_format}[vout]")
    return ";".join(nodes)

def build_ffmpeg_command(flat: FlatTimeline, specification: RenderSpecification, media_paths: dict[str, str], ffmpeg_binary: str = "ffmpeg") -> list[str]:
    ordered_ids = []
    for item in flat.video_layers:
        if item.layer.source_id and item.layer.source_id not in ordered_ids:
            ordered_ids.append(item.layer.source_id)
    missing = [asset_id for asset_id in ordered_ids if asset_id not in media_paths]
    if missing:
        raise ValueError(f"missing media paths: {missing}")
    input_indices = {asset_id: i for i, asset_id in enumerate(ordered_ids)}
    command = [ffmpeg_binary, "-y" if specification.overwrite else "-n"]
    for asset_id in ordered_ids:
        command.extend(["-i", media_paths[asset_id]])
    command.extend([
        "-filter_complex", build_video_filter(flat, specification, input_indices),
        "-map", "[vout]", "-c:v", specification.video_codec,
        "-pix_fmt", specification.pixel_format, "-an", specification.output_path,
    ])
    return command

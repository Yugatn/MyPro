"""OTIO interchange adapter with explicit losses and relinking."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..errors import ImportErrorBase
from ..identity import hash_file
from .base import ImportAdapter, ImportResult
from .reports import ImportManifest, LossEntry, LossReport, MappingEntry, MappingReport, RelinkEntry, RelinkingReport, SourceDescriptor


class OTIOAdapter(ImportAdapter):
    adapter_id = "otio_adapter"
    adapter_version = "0.1.0"
    source_format = "otio-compatible"
    supported_extensions = (".otio", ".xml", ".fcpxml", ".edl", ".aaf")

    def import_project(self, path: Path) -> ImportResult:
        try:
            import opentimelineio as otio
            timeline = otio.adapters.read_from_file(str(path))
        except Exception as exc:
            raise ImportErrorBase(f"OTIO import failed for {path}") from exc

        mappings: list[MappingEntry] = []
        losses: list[LossEntry] = []
        relinks: list[RelinkEntry] = []
        tracks: list[dict[str, Any]] = []
        clip_count = effect_count = marker_count = 0

        for track_index, track in enumerate(timeline.tracks):
            clips: list[dict[str, Any]] = []
            for item_index, item in enumerate(track):
                if not isinstance(item, otio.schema.Clip):
                    continue
                clip_count += 1
                clip_id = item.name or f"clip_{track_index}_{item_index}"
                mappings.append(MappingEntry("otio.Clip", clip_id, "mypro.montage.clip", clip_id, 1.0))

                media_reference = getattr(item, "media_reference", None)
                target_url = getattr(media_reference, "target_url", None) if media_reference else None
                if target_url:
                    candidate = Path(target_url)
                    exists = candidate.exists()
                    relinks.append(RelinkEntry(
                        target_url, str(candidate) if exists else None,
                        "path_match" if exists else "none", 1.0 if exists else 0.0,
                        "resolved" if exists else "placeholder",
                    ))
                    if not exists:
                        losses.append(LossEntry(
                            f"media:{clip_id}", "major",
                            "external media could not be resolved", "media placeholder",
                        ))

                effects = list(getattr(item, "effects", []) or [])
                effect_count += len(effects)
                if effects:
                    losses.append(LossEntry(
                        f"effects:{clip_id}", "major",
                        "effects have no canonical mapping", "clip without effects",
                    ))

                markers = list(getattr(item, "markers", []) or [])
                marker_count += len(markers)
                if markers:
                    losses.append(LossEntry(
                        f"markers:{clip_id}", "minor", "marker mapping is deferred",
                    ))

                source_range = item.source_range
                clips.append({
                    "id": clip_id,
                    "name": item.name,
                    "media_reference": {"target_url": target_url} if target_url else None,
                    "source_range": (
                        None if source_range is None else {
                            "start": {"num": int(source_range.start_time.value), "den": int(source_range.start_time.rate)},
                            "duration": {"num": int(source_range.duration.value), "den": int(source_range.duration.rate)},
                        }
                    ),
                })
            tracks.append({"kind": track.kind, "clips": clips})

        rate = getattr(getattr(timeline, "global_start_time", None), "rate", None)
        manifest = ImportManifest(
            source=SourceDescriptor(
                self.source_format, None, self.adapter_id, self.adapter_version,
                str(hash_file(path)), path.stat().st_size,
                datetime.now(timezone.utc).isoformat(timespec="microseconds"),
            ),
            mapping=MappingReport(tuple(mappings), ()),
            losses=LossReport(tuple(losses)),
            relinking=RelinkingReport(tuple(relinks)),
            statistics={"tracks": len(tracks), "clips": clip_count, "effects": effect_count, "markers": marker_count},
        )
        return self._new_result(
            manifest=manifest,
            canonical_candidate={
                "tracks": tracks,
                "timebase": {"num": int(rate), "den": 1} if rate else None,
            },
        )

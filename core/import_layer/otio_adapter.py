from __future__ import annotations
from pathlib import Path
from core.identity import hash_bytes
from .base import ImportResult, SourceDescriptor
from .manifest import ImportManifest, LossyTransformation


class OTIOAdapter:
    adapter_id="otio"
    adapter_version="0.1.0"
    supported_extensions=(".otio",".xml",".edl",".aaf")

    def import_project(self, path: Path) -> ImportResult:
        path=Path(path)
        raw=path.read_bytes()
        source_hash=hash_bytes(raw,algorithm="sha256")
        try:
            import opentimelineio as otio
        except ImportError as exc:
            raise RuntimeError("opentimelineio is required for project import") from exc
        timeline=otio.adapters.read_from_file(str(path))
        clips=[]
        tracks=[]
        for track in timeline.tracks:
            track_data={"name":track.name or "unnamed","kind":getattr(track,"kind",None),"clips":[]}
            for item in track:
                if isinstance(item, otio.schema.Clip):
                    sr=item.source_range
                    track_data["clips"].append({
                        "name":item.name,
                        "media_reference":str(item.media_reference),
                        "source_range": _range_dict(sr),
                    })
            tracks.append(track_data)
            clips.extend(track_data["clips"])
        manifest=ImportManifest(
            adapter_id=self.adapter_id,adapter_version=self.adapter_version,
            source_format=path.suffix.lower().lstrip("."),
            source_version=None,source_hash=str(source_hash),
            statistics={"tracks_imported":len(tracks),"clips_imported":len(clips)},
            mapping_rules_applied=["otio.timeline_to_canonical","otio.track_to_track","otio.clip_to_clip"],
        )
        if not clips:
            manifest.losses.append(LossyTransformation("clips","No OTIO clips were found","major"))
        return ImportResult(
            self.adapter_id,self.adapter_version,
            SourceDescriptor(str(path),source_hash,path.suffix.lower().lstrip(".")),
            {"name":timeline.name or path.stem,"tracks":tracks},
            manifest,
            tuple({"source":"otio","target":"canonical","element":"track"} for _ in tracks),
            ({"source_hash":str(source_hash),"adapter":self.adapter_id,"version":self.adapter_version},),
        )


def _range_dict(sr):
    if sr is None:
        return None
    return {
        "start": {"value":sr.start_time.value,"rate":sr.start_time.rate},
        "duration":{"value":sr.duration.value,"rate":sr.duration.rate},
    }

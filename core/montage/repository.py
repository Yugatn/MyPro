"""Event-backed montage repository."""
from __future__ import annotations
from dataclasses import replace
from core.project.events import EventLog
from .model import MediaAsset, Timeline, VideoLayer, VideoTrack, AudioTrack


class MontageRepository:
    def __init__(self, log: EventLog):
        self.log = log
        self.media_pool: dict[str, MediaAsset] = {}
        self.timelines: dict[str, Timeline] = {}
        self.active_timeline_id: str | None = None
        self._replay()

    def _record(self, event_type: str, payload: dict):
        event = self.log.append(type=event_type, payload=payload)
        self._apply(event.event_type, event.payload)
        return event

    def _replay(self):
        for event in self.log.iter_events():
            self._apply(event["event_type"], event["payload"])

    def _apply(self, event_type: str, payload: dict):
        # Repository persistence is intentionally compact in v0.4. The full
        # object is encoded in each mutation event, keeping replay deterministic.
        if event_type == "montage.asset_added":
            from core.identity import ContentHash
            from core.project.time import RationalTime
            d = payload["asset"]
            self.media_pool[d["id"]] = MediaAsset(
                id=d["id"], name=d["name"], content_hash=ContentHash.parse(d["content_hash"]),
                kind=d["kind"], duration=RationalTime(d["duration"]["num"], d["duration"]["den"]),
                width=d.get("width"), height=d.get("height"),
                fps_num=d.get("fps_num"), fps_den=d.get("fps_den"))
        elif event_type == "montage.timeline_created":
            self.timelines[payload["timeline"]["id"]] = _timeline_from_dict(payload["timeline"])
            self.active_timeline_id = self.active_timeline_id or payload["timeline"]["id"]
        elif event_type == "montage.timeline_state":
            tl = _timeline_from_dict(payload["timeline"])
            self.timelines[tl.id] = tl
        elif event_type == "montage.timeline_active":
            self.active_timeline_id = payload["timeline_id"]

    def add_asset(self, asset: MediaAsset):
        if asset.id in self.media_pool:
            raise ValueError(f"asset exists: {asset.id}")
        self._record("montage.asset_added", {"asset": _asset_dict(asset)})

    def create_timeline(self, timeline: Timeline):
        if timeline.id in self.timelines:
            raise ValueError(f"timeline exists: {timeline.id}")
        self._record("montage.timeline_created", {"timeline": _timeline_dict(timeline)})

    def _set(self, timeline: Timeline):
        self._record("montage.timeline_state", {"timeline": _timeline_dict(timeline)})

    def add_video_layer(self, timeline_id: str, track_id: str, layer: VideoLayer):
        tl = self.timelines[timeline_id]
        track = next(t for t in tl.video_tracks if t.id == track_id)
        tracks = tuple(track.with_layers(track.layers + (layer,)) if t.id == track_id else t for t in tl.video_tracks)
        self._set(tl.with_video_tracks(tracks))

    def add_video_track(self, timeline_id: str, name: str | None = None):
        tl = self.timelines[timeline_id]
        idx = len(tl.video_tracks)
        track = VideoTrack(_id("vt"), idx, name or f"V{idx+1}")
        self._set(tl.with_video_tracks(tl.video_tracks + (track,)))
        return self.timelines[timeline_id].video_tracks[-1]

    def add_audio_track(self, timeline_id: str, name: str | None = None):
        tl = self.timelines[timeline_id]
        idx = len(tl.audio_tracks)
        track = AudioTrack(_id("at"), idx, name or f"A{idx+1}")
        self._set(tl.with_audio_tracks(tl.audio_tracks + (track,)))
        return self.timelines[timeline_id].audio_tracks[-1]

    def validate(self):
        from .validation import validate_timeline
        for tl in self.timelines.values():
            validate_timeline(tl)
        return True


def _id(prefix: str) -> str:
    import uuid
    return f"{prefix}_{uuid.uuid4().hex}"


def _asset_dict(a: MediaAsset) -> dict:
    return {"id":a.id,"name":a.name,"content_hash":str(a.content_hash),"kind":a.kind,
            "duration":a.duration.to_dict(),"width":a.width,"height":a.height,
            "fps_num":a.fps_num,"fps_den":a.fps_den}


def _layer_dict(l: VideoLayer) -> dict:
    return {"id":l.id,"kind":l.kind.value,"name":l.name,
            "range":{"start":l.range.start.to_dict(),"end":l.range.end.to_dict()},
            "source_id":l.source_id,"nested_timeline_id":l.nested_timeline_id}


def _timeline_dict(t: Timeline) -> dict:
    return {"id":t.id,"name":t.name,"fps_num":t.fps_num,"fps_den":t.fps_den,
            "parent_timeline_id":t.parent_timeline_id,"audio_sample_rate":t.audio_sample_rate,
            "video_tracks":[{"id":x.id,"index":x.index,"name":x.name,"layers":[_layer_dict(l) for l in x.layers]} for x in t.video_tracks],
            "audio_tracks":[{"id":x.id,"index":x.index,"name":x.name,"layers":[]} for x in t.audio_tracks]}


def _rt(d):
    from core.project.time import RationalTime
    return RationalTime(d["num"], d["den"])


def _timeline_from_dict(d):
    from core.project.time import TimeRange
    from .model import LayerKind, VideoLayer
    v=[]
    for td in d["video_tracks"]:
        layers=tuple(VideoLayer(id=x["id"],kind=LayerKind(x["kind"]),name=x["name"],
            range=TimeRange(_rt(x["range"]["start"]),_rt(x["range"]["end"])),
            source_id=x.get("source_id"),nested_timeline_id=x.get("nested_timeline_id")) for x in td["layers"])
        v.append(VideoTrack(td["id"],td["index"],td["name"],layers))
    a=[AudioTrack(x["id"],x["index"],x["name"],()) for x in d["audio_tracks"]]
    return Timeline(d["id"],d["name"],d["fps_num"],d["fps_den"],tuple(v),tuple(a),
                    d.get("parent_timeline_id"),d.get("audio_sample_rate",48000))

"""Platform-neutral viewer/editor interaction model."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.project.time import RationalTime, TimeRange


class ViewerMode(str, Enum):
    WATCH = "watch"
    SELECT = "select"
    EDIT = "edit"


class ViewerAction(str, Enum):
    MARK_FRAGMENT = "mark_fragment"
    ADD_TO_MONTAGE = "add_to_montage"
    TRIM_SELECTION = "trim_selection"
    CREATE_CLIP = "create_clip"
    COMMENT = "comment"


@dataclass(frozen=True)
class ViewerSelection:
    content_id: str
    published_version_id: str | None
    time_range: TimeRange

    @property
    def start(self) -> RationalTime:
        return self.time_range.start

    @property
    def end(self) -> RationalTime:
        return self.time_range.end


@dataclass(frozen=True)
class ViewerIntent:
    action: ViewerAction
    selection: ViewerSelection
    request_id: str
    actor_id: str
    note: str | None = None

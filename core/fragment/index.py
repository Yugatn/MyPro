"""Deterministic in-memory index for reusable content fragments."""
from __future__ import annotations
from dataclasses import dataclass, field
from core.fragment.model import ContentFragment, FragmentKind
from core.project.time import TimeRange

@dataclass
class FragmentIndex:
    _items: dict[str, ContentFragment] = field(default_factory=dict)

    def add(self, fragment: ContentFragment) -> None:
        if fragment.id in self._items:
            raise ValueError(f"duplicate fragment id: {fragment.id}")
        self._items[fragment.id] = fragment

    def get(self, fragment_id: str) -> ContentFragment:
        return self._items[fragment_id]

    def all(self) -> tuple[ContentFragment, ...]:
        return tuple(self._items.values())

    def by_kind(self, kind: FragmentKind) -> tuple[ContentFragment, ...]:
        return tuple(f for f in self._items.values() if f.kind is kind)

    def by_source(self, source_content_id: str) -> tuple[ContentFragment, ...]:
        return tuple(f for f in self._items.values() if f.source_content_id == source_content_id)

    def overlapping(self, time_range: TimeRange, *, source_content_id: str | None = None) -> tuple[ContentFragment, ...]:
        def overlaps(a: TimeRange, b: TimeRange) -> bool:
            return a.start.fraction < b.end.fraction and b.start.fraction < a.end.fraction
        return tuple(
            f for f in self._items.values()
            if (source_content_id is None or f.source_content_id == source_content_id)
            and overlaps(f.time_range, time_range)
        )

    def by_label(self, label: str) -> tuple[ContentFragment, ...]:
        needle = label.casefold()
        return tuple(f for f in self._items.values() if f.label and needle in f.label.casefold())

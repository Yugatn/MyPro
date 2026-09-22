"""Exact canonical project time and synchronization domains."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True, order=True)
class RationalTime:
    numerator: int
    denominator: int = 1

    def __post_init__(self) -> None:
        if self.denominator <= 0:
            raise ValueError("denominator must be positive")

    @property
    def fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    def to_seconds(self) -> float:
        return float(self.fraction)

    def to_dict(self) -> dict[str, int]:
        return {"num": self.numerator, "den": self.denominator}


@dataclass(frozen=True)
class TimeRange:
    start: RationalTime
    end: RationalTime

    def __post_init__(self) -> None:
        if self.end.fraction <= self.start.fraction:
            raise ValueError("end must be greater than start")

    @property
    def duration(self) -> Fraction:
        return self.end.fraction - self.start.fraction

    def contains(self, value: RationalTime) -> bool:
        return self.start.fraction <= value.fraction < self.end.fraction


@dataclass(frozen=True)
class ClockRef:
    clock_id: str
    epoch: str
    rate_hz: RationalTime | None = None


@dataclass(frozen=True)
class SyncPoint:
    clock: ClockRef
    media_time: RationalTime
    clock_time: RationalTime


@dataclass(frozen=True)
class SyncGroup:
    id: str
    members: tuple[str, ...]
    sync_points: tuple[SyncPoint, ...]
    external_clock: ClockRef | None = None

    def __post_init__(self) -> None:
        if not self.members:
            raise ValueError("sync group must contain at least one member")
        if len(set(self.members)) != len(self.members):
            raise ValueError("sync group members must be unique")

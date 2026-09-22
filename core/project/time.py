"""Exact project time primitives.

Canonical time is rational. Float seconds are an interchange convenience only.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True, order=True)
class RationalTime:
    """An exact time value represented as numerator/denominator."""

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
    """Half-open interval [start, end)."""

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

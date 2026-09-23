"""Exact rational project time."""
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

    def to_seconds(self) -> Fraction:
        return self.fraction

    def to_dict(self) -> dict[str, int]:
        f = self.fraction
        return {"num": f.numerator, "den": f.denominator}

    @classmethod
    def from_seconds(cls, value: Fraction | int) -> "RationalTime":
        f = Fraction(value)
        return cls(f.numerator, f.denominator)

    def __add__(self, other: "RationalTime") -> "RationalTime":
        return self.from_seconds(self.fraction + other.fraction)

    def __sub__(self, other: "RationalTime") -> "RationalTime":
        return self.from_seconds(self.fraction - other.fraction)


@dataclass(frozen=True)
class TimeRange:
    start: RationalTime
    end: RationalTime

    def __post_init__(self) -> None:
        if self.end.fraction <= self.start.fraction:
            raise ValueError("end must be greater than start")

    @property
    def duration(self) -> RationalTime:
        return RationalTime.from_seconds(self.end.fraction - self.start.fraction)

    def contains(self, value: RationalTime) -> bool:
        return self.start.fraction <= value.fraction < self.end.fraction

from fractions import Fraction
import pytest
from core.project.time import RationalTime,TimeRange

def test_exact_arithmetic():
    a=RationalTime.from_seconds(Fraction(1,3)); b=RationalTime.from_seconds(Fraction(2,3))
    assert (a+b).to_seconds()==1
    assert (b-a).to_seconds()==Fraction(1,3)

def test_half_open():
    r=TimeRange(RationalTime(0),RationalTime(1))
    assert r.contains(RationalTime(0)); assert not r.contains(RationalTime(1))

def test_invalid():
    with pytest.raises(ValueError): TimeRange(RationalTime(1),RationalTime(1))

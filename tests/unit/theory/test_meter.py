from fractions import Fraction

import pytest

from russian_piano_composer.theory.meter import (
    MetricPosition,
    TimeSignature,
    get_metric_position,
)


def test_time_signature_valid():
    ts44 = TimeSignature(4, 4)
    assert ts44.numerator == 4
    assert ts44.denominator == 4
    assert ts44.bar_duration == Fraction(4)

    ts34 = TimeSignature(3, 4)
    assert ts34.bar_duration == Fraction(3)

    ts68 = TimeSignature(6, 8)
    assert ts68.bar_duration == Fraction(3)

    ts128 = TimeSignature(12, 8)
    assert ts128.bar_duration == Fraction(6)

    ts54 = TimeSignature(5, 4)
    assert ts54.bar_duration == Fraction(5)

    ts58 = TimeSignature(5, 8)
    assert ts58.bar_duration == Fraction(5, 2)


def test_time_signature_invalid():
    with pytest.raises(ValueError, match="Numerator must be a positive integer"):
        TimeSignature(0, 4)
    with pytest.raises(ValueError, match="Numerator must be a positive integer"):
        TimeSignature(-3, 4)
    with pytest.raises(ValueError, match="Denominator must be a positive integer"):
        TimeSignature(3, 0)
    with pytest.raises(ValueError, match="Denominator must be a power of 2"):
        TimeSignature(3, 3)
    with pytest.raises(ValueError, match="Denominator must be a power of 2"):
        TimeSignature(4, 5)


def test_metric_position_valid():
    mp = MetricPosition(bar_index=0, offset=Fraction(1, 2))
    assert mp.bar_index == 0
    assert mp.offset == Fraction(1, 2)


def test_metric_position_invalid():
    with pytest.raises(ValueError, match="bar_index must be a non-negative integer"):
        MetricPosition(-1, Fraction(0))
    with pytest.raises(ValueError, match=r"offset -1/2 cannot be negative"):
        MetricPosition(0, Fraction(-1, 2))


def test_get_metric_position_34():
    meter = TimeSignature(3, 4)  # bar duration = 3

    # Onset = 0 -> Bar 0, offset 0
    mp0 = get_metric_position(0, meter)
    assert mp0 == MetricPosition(0, Fraction(0))

    # Onset = 5/2 -> Bar 0, offset 5/2
    mp1 = get_metric_position(Fraction(5, 2), meter)
    assert mp1 == MetricPosition(0, Fraction(5, 2))

    # Onset = 3 -> Bar 1, offset 0
    mp2 = get_metric_position(3, meter)
    assert mp2 == MetricPosition(1, Fraction(0))

    # Onset = 13/2 -> Bar 2, offset 1/2 (13/2 = 6 + 1/2 = 2 * 3 + 1/2)
    mp3 = get_metric_position(Fraction(13, 2), meter)
    assert mp3 == MetricPosition(2, Fraction(1, 2))


def test_get_metric_position_68():
    meter = TimeSignature(6, 8)  # bar duration = 3

    mp = get_metric_position(Fraction(7, 2), meter)  # 7/2 = 3.5 = 1 bar + 0.5
    assert mp == MetricPosition(1, Fraction(1, 2))

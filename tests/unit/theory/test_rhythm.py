from fractions import Fraction

import pytest

from russian_piano_composer.theory.rhythm import (
    Duration,
    RhythmEvent,
    RhythmSkeleton,
    TimePoint,
    dotted,
    subdivide,
    tuplet,
    validate_bar_fill,
)


def test_duration_valid():
    d1 = Duration(Fraction(1, 2))
    d2 = Duration(Fraction(2, 4))
    assert d1 == d2
    assert d1.value == Fraction(1, 2)

    # Int input
    d3 = Duration(1)
    assert d3.value == Fraction(1)


def test_duration_invalid():
    with pytest.raises(ValueError, match=r"Duration value 0 must be positive"):
        Duration(0)
    with pytest.raises(ValueError, match=r"Duration value -1/2 must be positive"):
        Duration(Fraction(-1, 2))
    with pytest.raises(TypeError, match="Duration value must be Fraction or int"):
        Duration(0.5)  # type: ignore[arg-type]


def test_duration_arithmetic():
    d1 = Duration(Fraction(1, 2))
    d2 = Duration(Fraction(1, 4))
    assert d1 + d2 == Duration(Fraction(3, 4))
    assert d1 - d2 == Duration(Fraction(1, 4))
    assert d1 * 2 == Duration(1)
    assert 2 * d1 == Duration(1)
    assert d1 / 2 == Duration(Fraction(1, 4))


def test_timepoint_valid():
    t0 = TimePoint(0)
    t1 = TimePoint(Fraction(1, 2))
    assert t0.value == Fraction(0)
    assert t1.value == Fraction(1, 2)


def test_timepoint_invalid():
    with pytest.raises(ValueError, match=r"TimePoint value -1 cannot be negative"):
        TimePoint(-1)
    with pytest.raises(TypeError, match="TimePoint value must be Fraction or int"):
        TimePoint(1.5)  # type: ignore[arg-type]


def test_timepoint_arithmetic():
    t0 = TimePoint(0)
    d = Duration(Fraction(1, 2))
    t1 = t0 + d
    assert isinstance(t1, TimePoint)
    assert t1.value == Fraction(1, 2)

    diff = t1 - t0
    assert isinstance(diff, Duration)
    assert diff.value == Fraction(1, 2)

    with pytest.raises(ValueError, match="Difference between TimePoints must be positive"):
        _ = t0 - t1


def test_rhythmevent_valid():
    ev = RhythmEvent(onset=0, duration=Fraction(1, 2), accent=True)
    assert ev.onset == Fraction(0)
    assert ev.duration == Fraction(1, 2)
    assert ev.end == Fraction(1, 2)
    assert ev.accent is True
    assert ev.tie is False


def test_rhythmevent_invalid():
    with pytest.raises(ValueError, match=r"Onset -1 cannot be negative"):
        RhythmEvent(-1, Fraction(1, 2))
    with pytest.raises(ValueError, match=r"Duration 0 must be positive"):
        RhythmEvent(0, 0)


def test_rhythm_skeleton_valid():
    ev1 = RhythmEvent(0, Fraction(1, 2))
    ev2 = RhythmEvent(Fraction(1, 2), Fraction(1, 2))
    skel = RhythmSkeleton([ev1, ev2])
    assert len(skel) == 2
    assert skel[0] == ev1
    assert skel[1] == ev2

    # Skeleton with gaps (rests)
    ev3 = RhythmEvent(2, Fraction(1))
    skel_gap = RhythmSkeleton([ev1, ev3])
    assert len(skel_gap) == 2


def test_rhythm_skeleton_invalid():
    ev1 = RhythmEvent(0, Fraction(1))
    ev_overlap = RhythmEvent(Fraction(1, 2), Fraction(1, 2))
    with pytest.raises(ValueError, match="Overlapping events detected"):
        RhythmSkeleton([ev1, ev_overlap])

    ev_first = RhythmEvent(2, Fraction(1))
    ev_unordered = RhythmEvent(0, Fraction(1, 2))
    with pytest.raises(ValueError, match="Events must be ordered by onset"):
        RhythmSkeleton([ev_first, ev_unordered])


def test_subdivide():
    subs2 = subdivide(1, 2)
    assert subs2 == (Fraction(1, 2), Fraction(1, 2))
    assert sum(subs2) == Fraction(1)

    subs3 = subdivide(1, 3)
    assert subs3 == (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3))
    assert sum(subs3) == Fraction(1)

    with pytest.raises(ValueError, match="Subdivision count n must be a positive integer"):
        subdivide(1, 0)


def test_dotted():
    assert dotted(1, 0) == Fraction(1)
    assert dotted(1, 1) == Fraction(3, 2)  # quarter + 1 dot = 3/2
    assert dotted(1, 2) == Fraction(7, 4)  # quarter + 2 dots = 7/4
    assert dotted(2, 1) == Fraction(3)     # half + 1 dot = 3

    with pytest.raises(ValueError, match="Dots count must be a non-negative integer"):
        dotted(1, -1)


def test_tuplet():
    # 3:2 triplet (3 notes in space of 2 eighth notes)
    # Eighth note = 1/2. 3:2 triplet scaled eighth = 1/2 * 2/3 = 1/3
    eighth = Fraction(1, 2)
    triplet_eighth = tuplet(eighth, 3, 2)
    assert triplet_eighth == Fraction(1, 3)
    assert triplet_eighth * 3 == Fraction(1)

    # 5:4 quintuplet
    quarter = Fraction(1)
    quint_quarter = tuplet(quarter, 5, 4)
    assert quint_quarter == Fraction(4, 5)


def test_validate_bar_fill():
    # 3/4 bar = 3
    ev1 = RhythmEvent(0, Fraction(1))
    ev2 = RhythmEvent(1, Fraction(1))
    ev3 = RhythmEvent(2, Fraction(1))
    assert validate_bar_fill([ev1, ev2, ev3], 3) is True

    # Incomplete bar
    assert validate_bar_fill([ev1, ev2], 3) is False

    # Triplet bar fill in 1 beat
    t1 = RhythmEvent(0, Fraction(1, 3))
    t2 = RhythmEvent(Fraction(1, 3), Fraction(1, 3))
    t3 = RhythmEvent(Fraction(2, 3), Fraction(1, 3))
    assert validate_bar_fill([t1, t2, t3], 1) is True

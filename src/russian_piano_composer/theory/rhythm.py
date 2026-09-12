"""
Exact symbolic rhythm primitives and rational arithmetic utilities.
"""
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction


def _to_fraction(val: Fraction | int, name: str) -> Fraction:
    if isinstance(val, bool) or not isinstance(val, (Fraction, int)):
        raise TypeError(f"{name} must be Fraction or int, got {type(val).__name__}.")
    return Fraction(val)


@dataclass(frozen=True, slots=True)
class Duration:
    """
    Exact musical duration representation.
    """
    value: Fraction

    def __init__(self, value: Fraction | int) -> None:
        frac_val = _to_fraction(value, "Duration value")
        if frac_val <= 0:
            raise ValueError(f"Duration value {frac_val} must be positive.")
        object.__setattr__(self, "value", frac_val)

    def __add__(self, other: "Duration | Fraction | int") -> "Duration":
        if isinstance(other, Duration):
            return Duration(self.value + other.value)
        return Duration(self.value + _to_fraction(other, "Operand"))

    def __radd__(self, other: "Fraction | int") -> "Duration":
        return self.__add__(other)

    def __sub__(self, other: "Duration | Fraction | int") -> "Duration":
        other_val = other.value if isinstance(other, Duration) else _to_fraction(other, "Operand")
        return Duration(self.value - other_val)

    def __mul__(self, scalar: Fraction | int) -> "Duration":
        return Duration(self.value * _to_fraction(scalar, "Scalar"))

    def __rmul__(self, scalar: Fraction | int) -> "Duration":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Fraction | int) -> "Duration":
        return Duration(self.value / _to_fraction(scalar, "Scalar"))


@dataclass(frozen=True, slots=True)
class TimePoint:
    """
    Exact symbolic onset position representation.
    """
    value: Fraction

    def __init__(self, value: Fraction | int) -> None:
        frac_val = _to_fraction(value, "TimePoint value")
        if frac_val < 0:
            raise ValueError(f"TimePoint value {frac_val} cannot be negative.")
        object.__setattr__(self, "value", frac_val)

    def __add__(self, duration: Duration | Fraction | int) -> "TimePoint":
        dur_val = duration.value if isinstance(duration, Duration) else _to_fraction(duration, "Duration")
        return TimePoint(self.value + dur_val)

    def __radd__(self, duration: Duration | Fraction | int) -> "TimePoint":
        return self.__add__(duration)

    def __sub__(self, other: "TimePoint | Duration | Fraction | int") -> "TimePoint | Duration":
        if isinstance(other, TimePoint):
            diff = self.value - other.value
            if diff <= 0:
                raise ValueError("Difference between TimePoints must be positive to form a Duration.")
            return Duration(diff)
        dur_val = other.value if isinstance(other, Duration) else _to_fraction(other, "Duration")
        return TimePoint(self.value - dur_val)


@dataclass(frozen=True, slots=True)
class RhythmEvent:
    """
    Pitch-free symbolic rhythm event.
    """
    onset: Fraction
    duration: Fraction
    accent: bool = False
    tie: bool = False

    def __init__(
        self,
        onset: Fraction | int,
        duration: Fraction | int,
        accent: bool = False,
        tie: bool = False,
    ) -> None:
        frac_onset = _to_fraction(onset, "Onset")
        frac_duration = _to_fraction(duration, "Duration")
        if frac_onset < 0:
            raise ValueError(f"Onset {frac_onset} cannot be negative.")
        if frac_duration <= 0:
            raise ValueError(f"Duration {frac_duration} must be positive.")
        object.__setattr__(self, "onset", frac_onset)
        object.__setattr__(self, "duration", frac_duration)
        object.__setattr__(self, "accent", bool(accent))
        object.__setattr__(self, "tie", bool(tie))

    @property
    def end(self) -> Fraction:
        return self.onset + self.duration


@dataclass(frozen=True, slots=True)
class RhythmSkeleton:
    """
    Ordered monophonic rhythm event sequence.
    """
    events: tuple[RhythmEvent, ...]

    def __init__(self, events: Sequence[RhythmEvent]) -> None:
        event_tuple = tuple(events)
        for i in range(len(event_tuple)):
            curr = event_tuple[i]
            if not isinstance(curr, RhythmEvent):
                raise TypeError(f"Element at index {i} is not a RhythmEvent.")
            if i > 0:
                prev = event_tuple[i - 1]
                if curr.onset < prev.onset:
                    raise ValueError(
                        f"Events must be ordered by onset. Event {i} onset {curr.onset} < previous onset {prev.onset}."
                    )
                if curr.onset < prev.end:
                    raise ValueError(
                        f"Overlapping events detected. Event {i} onset {curr.onset} < previous event end {prev.end}."
                    )
        object.__setattr__(self, "events", event_tuple)

    def __len__(self) -> int:
        return len(self.events)

    def __getitem__(self, index: int) -> RhythmEvent:
        return self.events[index]


def subdivide(duration: Duration | Fraction | int, n: int) -> tuple[Fraction, ...]:
    """
    Divide a duration into n equal exact rational subdivisions.
    """
    dur_val = duration.value if isinstance(duration, Duration) else _to_fraction(duration, "Duration")
    if dur_val <= 0:
        raise ValueError(f"Duration {dur_val} must be positive.")
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError(f"Subdivision count n must be a positive integer, got {n}.")
    sub_val = dur_val / n
    return tuple(sub_val for _ in range(n))


def dotted(duration: Duration | Fraction | int, dots: int = 1) -> Fraction:
    """
    Compute exact duration with dots.
    D_n = D * (2 - 2^(-dots))
    """
    dur_val = duration.value if isinstance(duration, Duration) else _to_fraction(duration, "Duration")
    if dur_val <= 0:
        raise ValueError(f"Duration {dur_val} must be positive.")
    if not isinstance(dots, int) or isinstance(dots, bool) or dots < 0:
        raise ValueError(f"Dots count must be a non-negative integer, got {dots}.")
    if dots == 0:
        return dur_val
    multiplier = Fraction(2 * (2**dots) - 1, 2**dots)
    return dur_val * multiplier


def tuplet(duration: Duration | Fraction | int, a: int, b: int) -> Fraction:
    """
    Compute exact duration under an a:b tuplet ratio.
    a notes occupy the duration normally occupied by b notes.
    Scale ratio = b / a.
    """
    dur_val = duration.value if isinstance(duration, Duration) else _to_fraction(duration, "Duration")
    if dur_val <= 0:
        raise ValueError(f"Duration {dur_val} must be positive.")
    if not isinstance(a, int) or isinstance(a, bool) or a <= 0:
        raise ValueError(f"Tuplet parameter 'a' must be a positive integer, got {a}.")
    if not isinstance(b, int) or isinstance(b, bool) or b <= 0:
        raise ValueError(f"Tuplet parameter 'b' must be a positive integer, got {b}.")
    return dur_val * Fraction(b, a)


def validate_bar_fill(
    events: Sequence[RhythmEvent],
    expected_bar_duration: Duration | Fraction | int,
) -> bool:
    """
    Validate if a sequence of non-overlapping rhythm events exactly fills a bar duration.
    """
    target = (
        expected_bar_duration.value
        if isinstance(expected_bar_duration, Duration)
        else _to_fraction(expected_bar_duration, "expected_bar_duration")
    )
    if target <= 0:
        raise ValueError(f"Expected bar duration {target} must be positive.")
    if not events:
        return False

    try:
        skeleton = RhythmSkeleton(events)
    except (ValueError, TypeError):
        return False

    if skeleton[0].onset != Fraction(0):
        return False

    total_duration = sum((e.duration for e in skeleton.events), Fraction(0))
    return total_duration == target and skeleton.events[-1].end == target

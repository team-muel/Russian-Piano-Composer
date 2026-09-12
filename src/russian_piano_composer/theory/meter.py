"""
Exact meter and time signature primitives.
"""
from dataclasses import dataclass
from fractions import Fraction

from russian_piano_composer.theory.rhythm import TimePoint, _to_fraction


@dataclass(frozen=True, slots=True)
class TimeSignature:
    """
    Meter representation using exact rational bar duration.
    """
    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if not isinstance(self.numerator, int) or isinstance(self.numerator, bool) or self.numerator <= 0:
            raise ValueError(f"Numerator must be a positive integer, got {self.numerator}.")
        if not isinstance(self.denominator, int) or isinstance(self.denominator, bool) or self.denominator <= 0:
            raise ValueError(f"Denominator must be a positive integer, got {self.denominator}.")
        if (self.denominator & (self.denominator - 1)) != 0:
            raise ValueError(f"Denominator must be a power of 2, got {self.denominator}.")

    @property
    def bar_duration(self) -> Fraction:
        """
        Computed bar duration under canonical 1 = quarter note convention.
        B = N * (4 / D)
        """
        return Fraction(self.numerator * 4, self.denominator)


@dataclass(frozen=True, slots=True)
class MetricPosition:
    """
    Position within a measure under a given meter.
    """
    bar_index: int
    offset: Fraction

    def __init__(self, bar_index: int, offset: Fraction | int) -> None:
        if not isinstance(bar_index, int) or isinstance(bar_index, bool) or bar_index < 0:
            raise ValueError(f"bar_index must be a non-negative integer, got {bar_index}.")
        frac_offset = _to_fraction(offset, "offset")
        if frac_offset < 0:
            raise ValueError(f"offset {frac_offset} cannot be negative.")
        object.__setattr__(self, "bar_index", bar_index)
        object.__setattr__(self, "offset", frac_offset)


def get_metric_position(
    onset: TimePoint | Fraction | int,
    meter: TimeSignature,
) -> MetricPosition:
    """
    Compute measure index and offset within measure for an onset under constant meter.
    """
    if not isinstance(meter, TimeSignature):
        raise TypeError(f"meter must be a TimeSignature instance, got {type(meter).__name__}.")

    onset_val = onset.value if isinstance(onset, TimePoint) else _to_fraction(onset, "onset")
    if onset_val < 0:
        raise ValueError(f"Onset {onset_val} cannot be negative.")

    bar_dur = meter.bar_duration
    bar_index = int(onset_val // bar_dur)
    offset = onset_val % bar_dur

    return MetricPosition(bar_index, offset)

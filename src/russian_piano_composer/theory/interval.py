"""
Directed interval primitives, quality derivation, and pitch transposition.
"""
from dataclasses import dataclass

from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch

_DIATONIC_TO_LETTER: tuple[PitchLetter, ...] = tuple(
    sorted(PitchLetter, key=lambda p: p.diatonic_index)
)

# Reference semitones for simple diatonic steps 0..6
# 0: unison (P), 1: 2nd (M), 2: 3rd (M), 3: 4th (P), 4: 5th (P), 5: 6th (M), 6: 7th (M)
_PERFECT_DIATONIC_STEPS: set[int] = {0, 3, 4}
_SIMPLE_REF_SEMITONES: dict[int, int] = {
    0: 0,   # P1
    1: 2,   # M2
    2: 4,   # M3
    3: 5,   # P4
    4: 7,   # P5
    5: 9,   # M6
    6: 11,  # M7
}


@dataclass(frozen=True, slots=True)
class DirectedInterval:
    """
    Canonical musical interval preserving both diatonic displacement and chromatic semitones.
    """
    diatonic_steps: int
    semitones: int

    def __post_init__(self) -> None:
        if not isinstance(self.diatonic_steps, int) or isinstance(self.diatonic_steps, bool):
            raise TypeError(f"diatonic_steps must be an integer, got {type(self.diatonic_steps).__name__}.")
        if not isinstance(self.semitones, int) or isinstance(self.semitones, bool):
            raise TypeError(f"semitones must be an integer, got {type(self.semitones).__name__}.")

    @property
    def interval_number(self) -> int:
        """
        Ordinal interval number (e.g. 1 for unison, 3 for third, 8 for octave, 9 for ninth).
        """
        return abs(self.diatonic_steps) + 1

    @property
    def simple_number(self) -> int:
        """
        Simple ordinal interval number in range [1, 7].
        """
        return (abs(self.diatonic_steps) % 7) + 1

    @property
    def direction(self) -> int:
        """
        Interval direction: +1 for ascending, -1 for descending, 0 for unison/stationary.
        """
        if self.diatonic_steps > 0 or (self.diatonic_steps == 0 and self.semitones > 0):
            return 1
        if self.diatonic_steps < 0 or (self.diatonic_steps == 0 and self.semitones < 0):
            return -1
        return 0

    @property
    def quality(self) -> str:
        """
        Mathematical interval quality string (e.g., 'P1', 'm2', 'M3', 'A4', 'd5', 'P8', 'M9').
        Quality is independent of direction.
        """
        d_abs = abs(self.diatonic_steps)
        s_abs = abs(self.semitones)

        octaves = d_abs // 7
        d_simple = d_abs % 7
        s_ref = _SIMPLE_REF_SEMITONES[d_simple] + (12 * octaves)
        delta = s_abs - s_ref

        if d_simple in _PERFECT_DIATONIC_STEPS:
            if delta == 0:
                qual_prefix = "P"
            elif delta > 0:
                qual_prefix = "A" * delta
            else:
                qual_prefix = "d" * abs(delta)
        else:
            if delta == 0:
                qual_prefix = "M"
            elif delta == -1:
                qual_prefix = "m"
            elif delta > 0:
                qual_prefix = "A" * delta
            else:
                # delta <= -2
                qual_prefix = "d" * (abs(delta) - 1)

        return f"{qual_prefix}{self.interval_number}"

    def __str__(self) -> str:
        dir_str = "+" if self.direction > 0 else ("-" if self.direction < 0 else "")
        return f"{dir_str}{self.quality}"


def interval_between(source: SpelledPitch, target: SpelledPitch) -> DirectedInterval:
    """
    Compute canonical directed interval between two spelled pitches.
    """
    if not isinstance(source, SpelledPitch):
        raise TypeError(f"source must be a SpelledPitch instance, got {type(source).__name__}.")
    if not isinstance(target, SpelledPitch):
        raise TypeError(f"target must be a SpelledPitch instance, got {type(target).__name__}.")

    source_diatonic_total = (source.octave * 7) + source.letter.diatonic_index
    target_diatonic_total = (target.octave * 7) + target.letter.diatonic_index

    diatonic_steps = target_diatonic_total - source_diatonic_total
    semitones = target.midi - source.midi

    return DirectedInterval(diatonic_steps=diatonic_steps, semitones=semitones)


def transpose(pitch: SpelledPitch, interval: DirectedInterval) -> SpelledPitch:
    """
    Transpose a SpelledPitch by a DirectedInterval while preserving diatonic target letter and accidental alteration.
    """
    if not isinstance(pitch, SpelledPitch):
        raise TypeError(f"pitch must be a SpelledPitch instance, got {type(pitch).__name__}.")
    if not isinstance(interval, DirectedInterval):
        raise TypeError(f"interval must be a DirectedInterval instance, got {type(interval).__name__}.")

    source_diatonic_total = (pitch.octave * 7) + pitch.letter.diatonic_index
    target_diatonic_total = source_diatonic_total + interval.diatonic_steps

    target_octave = target_diatonic_total // 7
    target_letter_idx = target_diatonic_total % 7
    target_letter = _DIATONIC_TO_LETTER[target_letter_idx]

    target_midi = pitch.midi + interval.semitones
    natural_midi = 12 * (target_octave + 1) + target_letter.natural_pitch_class
    alteration = target_midi - natural_midi

    result = SpelledPitch(letter=target_letter, alteration=alteration, octave=target_octave)

    # Verify interval round-trip
    derived_interval = interval_between(pitch, result)
    if derived_interval != interval:
        raise ValueError(
            f"Transposition round-trip failed: pitch {pitch} + interval {interval} resulted in {result}, "
            f"which derives interval {derived_interval}."
        )

    return result

"""
Canonical spelled pitch representations and pitch class primitives.
"""
from dataclasses import dataclass
from enum import Enum


class PitchLetter(Enum):
    """
    The seven diatonic pitch letters with their diatonic indices and natural pitch classes.
    """
    C = (0, 0)
    D = (1, 2)
    E = (2, 4)
    F = (3, 5)
    G = (4, 7)
    A = (5, 9)
    B = (6, 11)

    def __init__(self, diatonic_index: int, natural_pitch_class: int) -> None:
        self._diatonic_index = diatonic_index
        self._natural_pitch_class = natural_pitch_class

    @property
    def diatonic_index(self) -> int:
        return self._diatonic_index

    @property
    def natural_pitch_class(self) -> int:
        return self._natural_pitch_class


def _alteration_to_accidental_str(alteration: int) -> str:
    if alteration == 0:
        return ""
    if alteration > 0:
        return "#" * alteration
    return "b" * abs(alteration)


@dataclass(frozen=True, slots=True)
class SpelledPitchClass:
    """
    Pitch class defined by diatonic letter and accidental alteration.
    Preserves spelling under structural equality (e.g. C# != Db).
    """
    letter: PitchLetter
    alteration: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.letter, PitchLetter):
            raise TypeError(f"letter must be a PitchLetter instance, got {type(self.letter).__name__}.")
        if not isinstance(self.alteration, int) or isinstance(self.alteration, bool):
            raise TypeError(f"alteration must be an integer, got {type(self.alteration).__name__}.")

    @property
    def pitch_class(self) -> int:
        """
        Sounding pitch class in [0, 11].
        """
        return (self.letter.natural_pitch_class + self.alteration) % 12

    def __str__(self) -> str:
        return f"{self.letter.name}{_alteration_to_accidental_str(self.alteration)}"


@dataclass(frozen=True, slots=True)
class SpelledPitch:
    """
    Canonical spelled pitch with letter, accidental alteration, and scientific octave.
    """
    letter: PitchLetter
    alteration: int = 0
    octave: int = 4

    def __post_init__(self) -> None:
        if not isinstance(self.letter, PitchLetter):
            raise TypeError(f"letter must be a PitchLetter instance, got {type(self.letter).__name__}.")
        if not isinstance(self.alteration, int) or isinstance(self.alteration, bool):
            raise TypeError(f"alteration must be an integer, got {type(self.alteration).__name__}.")
        if not isinstance(self.octave, int) or isinstance(self.octave, bool):
            raise TypeError(f"octave must be an integer, got {type(self.octave).__name__}.")

        calculated_midi = 12 * (self.octave + 1) + self.letter.natural_pitch_class + self.alteration
        if not (0 <= calculated_midi <= 127):
            raise ValueError(
                f"Spelled pitch {self} yields MIDI {calculated_midi}, which is outside valid range [0, 127]."
            )

    @property
    def midi(self) -> int:
        """
        Sounding MIDI note number in [0, 127].
        """
        return 12 * (self.octave + 1) + self.letter.natural_pitch_class + self.alteration

    @property
    def spelled_pitch_class(self) -> SpelledPitchClass:
        """
        Associated SpelledPitchClass.
        """
        return SpelledPitchClass(self.letter, self.alteration)

    def same_sounding_pitch(self, other: "SpelledPitch") -> bool:
        """
        Returns True if two spelled pitches produce the exact same sounding MIDI pitch.
        """
        if not isinstance(other, SpelledPitch):
            return False
        return self.midi == other.midi

    def __str__(self) -> str:
        acc_str = _alteration_to_accidental_str(self.alteration)
        return f"{self.letter.name}{acc_str}{self.octave}"

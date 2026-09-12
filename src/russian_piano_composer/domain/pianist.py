"""
Core ergonomic and pianist profile models.
"""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PianistProfile:
    """
    Physical and technical profile constraints for playability evaluation.

    Contains no universal ergonomic defaults (e.g. hand size).
    """
    target_level: str
    comfortable_span_semitones: int
    maximum_span_semitones: int
    maximum_simultaneous_notes_per_hand: int
    allow_hand_crossing: bool
    allow_rolled_chords: bool

    def __post_init__(self) -> None:
        if self.comfortable_span_semitones < 0:
            raise ValueError("comfortable_span_semitones must be non-negative.")

        if self.maximum_span_semitones < 0:
            raise ValueError("maximum_span_semitones must be non-negative.")

        if self.comfortable_span_semitones > self.maximum_span_semitones:
            raise ValueError("comfortable_span_semitones cannot exceed maximum_span_semitones.")

        if self.maximum_simultaneous_notes_per_hand <= 0:
            raise ValueError("maximum_simultaneous_notes_per_hand must be positive.")

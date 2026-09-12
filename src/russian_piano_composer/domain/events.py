"""
Core event primitives for the Russian Piano Composer.
"""
from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True, slots=True)
class ThemeEvent:
    """
    A canonical monophonic musical event within a theme.
    
    This represents symbolic musical information independent of serialization
    formats like MIDI or MusicXML.
    """
    midi: int
    onset: Fraction
    duration: Fraction
    metric_position: Fraction
    metric_strength: float
    accent: bool

    def __post_init__(self) -> None:
        if not (0 <= self.midi <= 127):
            raise ValueError(f"MIDI pitch {self.midi} must be between 0 and 127.")
        if self.onset < 0:
            raise ValueError(f"Onset {self.onset} cannot be negative.")
        if self.duration <= 0:
            raise ValueError(f"Duration {self.duration} must be positive.")
        if self.metric_position < 0:
            raise ValueError(f"Metric position {self.metric_position} cannot be negative.")
        if not (0.0 <= self.metric_strength <= 1.0):
            raise ValueError(f"Metric strength {self.metric_strength} must be in [0, 1].")

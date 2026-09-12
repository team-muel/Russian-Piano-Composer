"""
Core structural containers for generated themes.
"""
from dataclasses import dataclass

from .events import ThemeEvent
from .scores import ThemeScores


@dataclass(frozen=True, slots=True)
class Theme:
    """
    An ordered thematic object containing molecular musical events.
    """
    events: tuple[ThemeEvent, ...]
    tonic_pc: int
    mode: str
    meter_num: int
    meter_den: int
    bars: int
    archetype: str
    seed: int

    def __post_init__(self) -> None:
        if not self.events:
            raise ValueError("Theme must contain at least one event.")

        if not (0 <= self.tonic_pc <= 11):
            raise ValueError(f"Tonic pitch class {self.tonic_pc} must be in [0, 11].")

        if self.meter_num <= 0:
            raise ValueError(f"Meter numerator {self.meter_num} must be positive.")

        if self.meter_den <= 0:
            raise ValueError(f"Meter denominator {self.meter_den} must be positive.")

        if self.bars <= 0:
            raise ValueError(f"Bars {self.bars} must be positive.")

        # Verify event ordering
        for i in range(1, len(self.events)):
            if self.events[i].onset < self.events[i-1].onset:
                raise ValueError("Events must be strictly ordered by onset.")

@dataclass(frozen=True, slots=True)
class ScoredTheme:
    """
    A theme paired with its evaluation scores.
    """
    theme: Theme
    scores: ThemeScores

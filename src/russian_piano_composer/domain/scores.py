"""
Core score containers for evaluated themes.
"""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ThemeScores:
    """
    Immutable container for critic evaluation scores of a theme.
    """
    russian_style: float
    developability: float
    memorability: float
    harmonic_affordance: float
    novelty: float
    coherence: float
    copy_risk: float
    constraint_penalty: float

    def __post_init__(self) -> None:
        normalized_fields = [
            "russian_style", "developability", "memorability",
            "harmonic_affordance", "novelty", "coherence", "copy_risk"
        ]

        for field in normalized_fields:
            val = getattr(self, field)
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"Score {field} must be in [0, 1], got {val}")

        if self.constraint_penalty < 0.0:
            raise ValueError(f"Constraint penalty must be non-negative, got {self.constraint_penalty}")

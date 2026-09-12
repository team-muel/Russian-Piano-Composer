"""
Core generation result containers.
"""
from dataclasses import dataclass

from .dna import ThemeDNA
from .theme import ScoredTheme


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """
    Immutable result container for a theme generation process.
    """
    best: ScoredTheme | None
    pareto_front: tuple[ScoredTheme, ...]
    candidates_evaluated: int
    dna: ThemeDNA
    seed: int

    def __post_init__(self) -> None:
        if self.candidates_evaluated < 1:
            raise ValueError(f"candidates_evaluated must be >= 1, got {self.candidates_evaluated}")

        if self.best is not None:
            if not self.pareto_front:
                raise ValueError("pareto_front cannot be empty if best is provided.")

            # Use identity/structural check for best in pareto_front
            if self.best not in self.pareto_front:
                raise ValueError("best must belong to pareto_front.")

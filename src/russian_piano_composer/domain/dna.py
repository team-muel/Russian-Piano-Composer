"""
Core DNA models describing high-level generative intent.
"""
import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ThemeDNA:
    """
    High-level generative intent for a theme.

    This defines target stylistic and structural boundaries, not the music itself.
    """
    # Character dimensions
    darkness: float
    lyricism: float
    mystery: float
    agitation: float

    # Stylistic dimensions
    chromaticism: float
    modal_strength: float

    # Complexity dimensions
    interval_complexity: float
    rhythmic_complexity: float

    # Structural dimensions
    repetition: float
    asymmetry: float
    hook_strength: float

    # Structural targets
    desired_events: int
    desired_range: int

    # Reference-space weighting (must sum to 1)
    medtner: float
    rachmaninoff: float
    scriabin: float

    # Identifier for character or archetype
    archetype_id: str

    def __post_init__(self) -> None:
        continuous_fields = [
            "darkness", "lyricism", "mystery", "agitation", "chromaticism",
            "modal_strength", "interval_complexity", "rhythmic_complexity",
            "repetition", "asymmetry", "hook_strength", "medtner", "rachmaninoff", "scriabin"
        ]

        for field in continuous_fields:
            val = getattr(self, field)
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"{field} must be in [0, 1], got {val}")

        weight_sum = self.medtner + self.rachmaninoff + self.scriabin
        if not math.isclose(weight_sum, 1.0, rel_tol=1e-5, abs_tol=1e-5):
            raise ValueError(f"Composer weights must sum to 1.0, got {weight_sum}")

        if self.desired_events <= 0:
            raise ValueError(f"desired_events must be positive, got {self.desired_events}")

        if self.desired_range <= 0:
            raise ValueError(f"desired_range must be positive, got {self.desired_range}")

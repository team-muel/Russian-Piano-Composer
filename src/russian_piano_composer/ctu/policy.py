"""
Policy models for CTU candidate generation, discovery ranking, and held-out validation.
"""

import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CTUDiscoveryPolicy:
    """
    Immutable configuration policy for CTU candidate discovery.
    """

    discovery_ratio: float = 0.60             # First 60% measures for discovery
    min_piece_measures: int = 12              # Minimum measures required for temporal held-out eligibility
    window_lengths: tuple[int, ...] = (1, 2, 3, 4, 6, 8)  # Multi-scale candidate measure lengths
    stride_measures: int = 1                  # Window sliding stride
    nms_overlap_threshold: float = 0.50       # Non-maximum suppression Jaccard overlap threshold
    max_retained_ctus: int = 5                # Top N CTUs retained per piece
    min_event_count: int = 3                  # Minimum note attacks required in a candidate segment
    evidence_threshold_e1: float = 0.30       # Minimum discovery recurrence score for E1 tier promotion

    # Heuristic similarity weights (classified as ENGINEERING_HEURISTIC)
    weight_melodic: float = 0.40
    weight_rhythmic: float = 0.30
    weight_texture: float = 0.15
    weight_pitchclass: float = 0.15

    def compute_policy_hash(self) -> str:
        """Deterministic SHA-256 hash of discovery policy semantics."""
        canonical = {
            "discovery_ratio": self.discovery_ratio,
            "min_piece_measures": self.min_piece_measures,
            "window_lengths": list(self.window_lengths),
            "stride_measures": self.stride_measures,
            "nms_overlap_threshold": self.nms_overlap_threshold,
            "max_retained_ctus": self.max_retained_ctus,
            "min_event_count": self.min_event_count,
            "evidence_threshold_e1": self.evidence_threshold_e1,
            "weight_melodic": self.weight_melodic,
            "weight_rhythmic": self.weight_rhythmic,
            "weight_texture": self.weight_texture,
            "weight_pitchclass": self.weight_pitchclass,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class CTUValidationPolicy:
    """
    Immutable configuration policy for held-out future-reuse validation.
    """

    permutation_iterations: int = 10000
    bootstrap_iterations: int = 10000
    random_seed: int = 42

    def compute_policy_hash(self) -> str:
        """Deterministic SHA-256 hash of validation policy semantics."""
        canonical = {
            "permutation_iterations": self.permutation_iterations,
            "bootstrap_iterations": self.bootstrap_iterations,
            "random_seed": self.random_seed,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

"""
Training-composer-balanced sample weighting policy for RC-010.

Computes sample weights per training fold such that each training composer contributes
equal total weight, preventing prolific composers (e.g. Chopin 56 pieces vs Tchaikovsky 12)
from dominating model fitting or scaling.
"""

import hashlib
import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ComposerWeightingPolicy:
    """
    Immutable policy specification for composer-balanced training sample weights.
    """

    formula_id: str = "INVERSE_COMPOSER_FREQUENCY_NORMALIZED"
    description: str = (
        "Each training composer is assigned equal aggregate sample weight. "
        "Piece weight = 1 / (n_pieces_for_composer * n_training_composers)."
    )

    def compute_policy_hash(self) -> str:
        """
        Deterministic SHA-256 hash of composer weighting policy semantics.
        """
        canonical = {
            "formula_id": self.formula_id,
            "description": self.description,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def compute_composer_weighting_policy_hash() -> str:
    """Convenience function returning SHA-256 hash of weighting policy."""
    return ComposerWeightingPolicy().compute_policy_hash()


def compute_composer_balanced_weights(training_piece_composers: Sequence[str]) -> tuple[float, ...]:
    """
    Calculate training-composer-balanced sample weights for a sequence of training piece composers.

    Formula:
        w_i = 1.0 / (count(composer_i) * num_distinct_composers)

    Guarantees:
      - Sum of weights for each training composer = 1.0 / num_distinct_composers
      - Total sum of all sample weights = 1.0
      - Prolific composers do not dominate fitting or scaling.
    """
    if not training_piece_composers:
        return ()

    counts = Counter(training_piece_composers)
    n_distinct = len(counts)

    weights: list[float] = []
    for comp in training_piece_composers:
        w = 1.0 / (float(counts[comp]) * float(n_distinct))
        weights.append(round(w, 8))

    return tuple(weights)

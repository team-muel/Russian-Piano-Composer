"""
Feature extraction policy model.

Encapsulates all semantic defaults for feature extraction across polyphonic scores.
"""
from dataclasses import dataclass
from enum import StrEnum


class TieAttackPolicy(StrEnum):
    """How tie continuations are handled during feature extraction."""

    EXCLUDE_CONTINUATIONS = "EXCLUDE_CONTINUATIONS"
    COUNT_EVERY_EVENT = "COUNT_EVERY_EVENT"


class MelodicTransitionPolicy(StrEnum):
    """Policy for selecting eligible melodic transitions in polyphonic scores."""

    VOICE_AWARE_SINGLE_NOTE_ONLY = "VOICE_AWARE_SINGLE_NOTE_ONLY"
    GLOBAL_ONSET_SORTED = "GLOBAL_ONSET_SORTED"


class GraceNotePolicy(StrEnum):
    """Policy for handling grace notes in structural feature calculations."""

    EXCLUDE = "EXCLUDE"
    INCLUDE = "INCLUDE"


class PitchWeightingPolicy(StrEnum):
    """Policy for weighting pitch observations."""

    ATTACK_UNWEIGHTED = "ATTACK_UNWEIGHTED"


@dataclass(frozen=True, slots=True)
class FeatureExtractionPolicy:
    """
    Immutable configuration policy for score feature extraction.
    """

    tie_policy: TieAttackPolicy = TieAttackPolicy.EXCLUDE_CONTINUATIONS
    melodic_policy: MelodicTransitionPolicy = MelodicTransitionPolicy.VOICE_AWARE_SINGLE_NOTE_ONLY
    grace_policy: GraceNotePolicy = GraceNotePolicy.EXCLUDE
    pitch_weighting: PitchWeightingPolicy = PitchWeightingPolicy.ATTACK_UNWEIGHTED
    require_single_note_voice: bool = True

    def compute_policy_hash(self) -> str:
        """
        Deterministic SHA-256 hash of feature extraction policy semantics.
        """
        import hashlib
        import json

        canonical = {
            "tie_policy": self.tie_policy.value,
            "melodic_policy": self.melodic_policy.value,
            "grace_policy": self.grace_policy.value,
            "pitch_weighting": self.pitch_weighting.value,
            "require_single_note_voice": self.require_single_note_voice,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


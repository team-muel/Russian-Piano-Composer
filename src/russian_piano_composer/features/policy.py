"""
Feature extraction policy model.

Encapsulates all semantic defaults for feature extraction across polyphonic scores.
"""
from dataclasses import dataclass
from enum import StrEnum


class TieAttackPolicy(StrEnum):
    """How tie continuations are handled during feature extraction."""

    EXCLUDE_CONTINUATIONS = "EXCLUDE_CONTINUATIONS"
    MERGE_TIES = "MERGE_TIES"
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
    DURATION_WEIGHTED = "DURATION_WEIGHTED"


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

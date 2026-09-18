"""
Candidate Thematic Unit (CTU) discovery and validation package init.
"""

from russian_piano_composer.ctu.controls import generate_matched_control
from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.models import (
    CTU_SCHEMA_VERSION,
    CTUCandidate,
    CTUDiscoveryResult,
    CTUValidationResult,
    EmpiricalCTUStatus,
    EvidenceTier,
    PieceValidationRecord,
    SegmentPosition,
    SegmentRepresentation,
    SegmentSpan,
)
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy, CTUValidationPolicy
from russian_piano_composer.ctu.representation import extract_segment_representation
from russian_piano_composer.ctu.segmentation import compute_temporal_split, generate_candidate_spans
from russian_piano_composer.ctu.similarity import compute_segment_similarity
from russian_piano_composer.ctu.validation import validate_ctu_future_reuse

__all__ = [
    "CTU_SCHEMA_VERSION",
    "CTUCandidate",
    "CTUDiscoveryPolicy",
    "CTUDiscoveryResult",
    "CTUValidationPolicy",
    "CTUValidationResult",
    "EmpiricalCTUStatus",
    "EvidenceTier",
    "PieceValidationRecord",
    "SegmentPosition",
    "SegmentRepresentation",
    "SegmentSpan",
    "compute_segment_similarity",
    "compute_temporal_split",
    "discover_ctus_for_score",
    "extract_segment_representation",
    "generate_candidate_spans",
    "generate_matched_control",
    "validate_ctu_future_reuse",
]

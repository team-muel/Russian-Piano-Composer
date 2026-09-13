"""
Domain models and schema definitions for Candidate Thematic Units (CTUs).

Provides immutable data structures for segment boundaries, multi-channel symbolic representations,
candidate records, discovery evidence, and held-out future-reuse validation results.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from fractions import Fraction

CTU_SCHEMA_VERSION: int = 1


class EvidenceTier(StrEnum):
    """Evidence classification tiers for Candidate Thematic Units."""

    E0_CANDIDATE_ONLY = "E0_CANDIDATE_ONLY"
    E1_DISCOVERY_RECURRENCE = "E1_DISCOVERY_RECURRENCE"
    E2_MULTICHANNEL_CONSENSUS = "E2_MULTICHANNEL_CONSENSUS"
    E3_HELDOUT_FUTURE_SUPPORTED = "E3_HELDOUT_FUTURE_SUPPORTED"


class EmpiricalCTUStatus(StrEnum):
    """Final empirical outcome status for CTU future-reuse validation."""

    CTU_VALIDATED = "CTU_VALIDATED"
    CTU_NOT_VALIDATED = "CTU_NOT_VALIDATED"
    CTU_INCONCLUSIVE = "CTU_INCONCLUSIVE"


@dataclass(frozen=True, slots=True)
class SegmentPosition:
    """Zero-based measure index and exact rational offset within the measure."""

    measure_index: int
    offset: Fraction = field(default_factory=lambda: Fraction(0))

    def __post_init__(self) -> None:
        if self.measure_index < 0:
            raise ValueError(f"measure_index must be >= 0, got {self.measure_index}")
        if self.offset < 0:
            raise ValueError(f"offset must be >= 0, got {self.offset}")


@dataclass(frozen=True, slots=True)
class SegmentSpan:
    """Exact score interval defined by start and end SegmentPosition."""

    start: SegmentPosition
    end: SegmentPosition

    def __post_init__(self) -> None:
        if self.end.measure_index < self.start.measure_index:
            raise ValueError(
                f"end measure ({self.end.measure_index}) precedes start measure ({self.start.measure_index})"
            )
        if self.end.measure_index == self.start.measure_index and self.end.offset <= self.start.offset:
            raise ValueError("end position must be strictly after start position in the same measure")

    @property
    def measure_span_count(self) -> int:
        """Number of complete or partial measures spanned."""
        return self.end.measure_index - self.start.measure_index + (1 if self.end.offset > 0 else 0)


@dataclass(frozen=True, slots=True)
class SegmentRepresentation:
    """
    Multi-channel symbolic representation of a score segment.
    Maintains separate evidence channels without polyphonic melody flattening.
    """

    melodic_intervals: tuple[tuple[int, ...], ...]  # Tuple of interval sequences per (staff, voice) stream
    rhythmic_ratios: tuple[Fraction, ...]            # IOI ratio sequence relative to beat unit
    texture_profile: tuple[int, ...]                 # Attack count per onset
    pitch_class_counts: tuple[int, ...]              # 12-bin pitch-class attack distribution

    def compute_semantic_hash(self) -> str:
        """Compute SHA-256 hash of representation contents."""
        import hashlib
        import json

        data = {
            "melodic_intervals": [list(stream) for stream in self.melodic_intervals],
            "rhythmic_ratios": [f"{r.numerator}/{r.denominator}" for r in self.rhythmic_ratios],
            "texture_profile": list(self.texture_profile),
            "pitch_class_counts": list(self.pitch_class_counts),
        }
        encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class CTUCandidate:
    """
    Candidate Thematic Unit record binding segment span, representation, and lineage hashes.
    """

    candidate_id: str
    piece_id: str
    corpus_id: str
    canonical_piece_hash: str
    span: SegmentSpan
    representation: SegmentRepresentation
    discovery_score: float = 0.0
    tier: EvidenceTier = EvidenceTier.E0_CANDIDATE_ONLY
    ctu_schema_version: int = CTU_SCHEMA_VERSION
    representation_hash: str = ""
    discovery_policy_hash: str = ""
    manifest_hash: str = ""

    def __post_init__(self) -> None:
        if not self.candidate_id:
            raise ValueError("candidate_id cannot be empty")
        if not self.piece_id:
            raise ValueError("piece_id cannot be empty")
        if not self.canonical_piece_hash:
            raise ValueError("canonical_piece_hash cannot be empty")


@dataclass(frozen=True, slots=True)
class CTUDiscoveryResult:
    """
    Discovery output record for a single score containing candidate CTUs and matched controls.
    """

    piece_id: str
    corpus_id: str
    canonical_piece_hash: str
    total_measures: int
    discovery_measures: int
    is_eligible: bool
    retained_ctus: tuple[CTUCandidate, ...]
    matched_controls: tuple[CTUCandidate, ...]
    raw_candidate_count: int
    post_dedup_candidate_count: int
    manifest_hash: str
    discovery_policy_hash: str


@dataclass(frozen=True, slots=True)
class PieceValidationRecord:
    """Future reuse validation metrics for a single eligible piece."""

    piece_id: str
    corpus_id: str
    ctu_mean_future_score: float
    control_mean_future_score: float
    difference: float


@dataclass(frozen=True, slots=True)
class CTUValidationResult:
    """
    Corpus-wide held-out future-reuse validation result summary.
    """

    total_pieces: int
    eligible_pieces: int
    ineligible_pieces: int
    piece_records: tuple[PieceValidationRecord, ...]
    mean_ctu_future_score: float
    mean_control_future_score: float
    mean_difference: float
    cohens_d: float
    bootstrap_ci_lower: float
    bootstrap_ci_upper: float
    permutation_p_value: float
    positive_effect_fraction: float
    empirical_status: EmpiricalCTUStatus
    manifest_hash: str
    discovery_policy_hash: str
    validation_policy_hash: str

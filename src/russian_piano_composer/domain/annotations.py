"""
Core domain models for curated theme annotations, half-open score spans, review state machines, and confidence levels.
"""
import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

THEME_ANNOTATION_SCHEMA_VERSION: int = 1


class ThemeRole(StrEnum):
    """
    Taxonomy for theme roles in structural piano analysis.
    """
    PRIMARY_THEME = "PRIMARY_THEME"
    SECONDARY_THEME = "SECONDARY_THEME"
    RECURRING_THEME = "RECURRING_THEME"
    MOTTO = "MOTTO"
    EPISODIC_THEME = "EPISODIC_THEME"
    OTHER_THEME = "OTHER_THEME"


class AnnotationStatus(StrEnum):
    """
    Explicit review state machine for theme annotations.
    """
    CANDIDATE = "CANDIDATE"
    REVIEWED = "REVIEWED"
    ACCEPTED = "ACCEPTED"
    DISPUTED = "DISPUTED"
    REJECTED = "REJECTED"
    STALE = "STALE"


class AnnotatorType(StrEnum):
    """
    Provenance of the annotation proposal.
    """
    HUMAN = "HUMAN"
    AI_ASSISTED_HUMAN = "AI_ASSISTED_HUMAN"
    ALGORITHM_CANDIDATE = "ALGORITHM_CANDIDATE"


class ReviewDecision(StrEnum):
    """
    Reviewer decision on an annotation.
    """
    APPROVE = "APPROVE"
    REQUEST_CHANGE = "REQUEST_CHANGE"
    DISAGREE = "DISAGREE"


class ReviewerType(StrEnum):
    """
    Category of the reviewer performing assessment.
    """
    SELF_REVIEW = "SELF_REVIEW"
    SECOND_HUMAN_REVIEW = "SECOND_HUMAN_REVIEW"
    AI_REVIEWER = "AI_REVIEWER"
    MUSIC_THEORY_REVIEWER = "MUSIC_THEORY_REVIEWER"


class EvidenceTag(StrEnum):
    """
    Structured evidence justification tags for thematic status.
    """
    INITIAL_PRESENTATION = "INITIAL_PRESENTATION"
    RECURRENCE = "RECURRENCE"
    DEVELOPMENTAL_REUSE = "DEVELOPMENTAL_REUSE"
    CADENTIAL_ARTICULATION = "CADENTIAL_ARTICULATION"
    PHRASE_COMPLETENESS = "PHRASE_COMPLETENESS"
    TEXTURAL_ARTICULATION = "TEXTURAL_ARTICULATION"
    SOURCE_ANNOTATION = "SOURCE_ANNOTATION"
    LITERATURE = "LITERATURE"
    OTHER = "OTHER"


class PieceReviewStatus(StrEnum):
    """
    Piece-level review outcome tracking.
    """
    UNREVIEWED = "UNREVIEWED"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEWED = "REVIEWED"
    NO_CLEAR_THEME = "NO_CLEAR_THEME"


@dataclass(frozen=True, slots=True)
class ScorePosition:
    """
    Exact rational score coordinate inside a canonical piece.
    """
    measure_index: int
    offset: Fraction

    def __post_init__(self) -> None:
        if not isinstance(self.measure_index, int) or self.measure_index < 0:
            raise ValueError(f"ScorePosition.measure_index must be a non-negative integer, got {self.measure_index!r}.")
        if not isinstance(self.offset, Fraction):
            if isinstance(self.offset, (int, str)):
                object.__setattr__(self, "offset", Fraction(self.offset))
            else:
                raise TypeError(f"ScorePosition.offset must be a Fraction, got {type(self.offset).__name__}.")
        if self.offset < 0:
            raise ValueError(f"ScorePosition.offset must be non-negative, got {self.offset}.")


@dataclass(frozen=True, slots=True)
class ThemeSpan:
    """
    Half-open interval [start, end) in canonical score time.
    The start boundary is inclusive; the end boundary is exclusive.
    """
    start: ScorePosition
    end: ScorePosition

    def __post_init__(self) -> None:
        if not isinstance(self.start, ScorePosition):
            raise TypeError(f"ThemeSpan.start must be ScorePosition, got {type(self.start).__name__}.")
        if not isinstance(self.end, ScorePosition):
            raise TypeError(f"ThemeSpan.end must be ScorePosition, got {type(self.end).__name__}.")

        if self.end.measure_index < self.start.measure_index:
            raise ValueError(
                f"Invalid ThemeSpan: end measure ({self.end.measure_index}) "
                f"precedes start measure ({self.start.measure_index})."
            )
        if (
            self.end.measure_index == self.start.measure_index
            and self.end.offset <= self.start.offset
        ):
            raise ValueError(
                f"Invalid ThemeSpan: same-measure end offset ({self.end.offset}) "
                f"must be strictly greater than start offset ({self.start.offset})."
            )


@dataclass(frozen=True, slots=True)
class ReviewRecord:
    """
    Audit record for a review action on a theme annotation.
    """
    reviewer_id: str
    reviewer_type: ReviewerType
    decision: ReviewDecision
    boundary_assessment: str | None = None
    role_assessment: str | None = None
    confidence_assessment: str | None = None
    notes: str | None = None
    reviewed_at: str | None = None

    def __post_init__(self) -> None:
        if not self.reviewer_id or not self.reviewer_id.strip():
            raise ValueError("ReviewRecord.reviewer_id cannot be empty.")
        if not isinstance(self.reviewer_type, ReviewerType):
            raise TypeError(f"Invalid reviewer_type {self.reviewer_type!r}.")
        if not isinstance(self.decision, ReviewDecision):
            raise TypeError(f"Invalid decision {self.decision!r}.")


@dataclass(frozen=True, slots=True)
class ThemeAnnotation:
    """
    Immutable representation of a theme annotation claim bound to exact canonical lineage.
    """
    annotation_id: str
    piece_id: str
    corpus_id: str
    score_entry_id: str
    span: ThemeSpan
    theme_role: ThemeRole
    confidence: int
    status: AnnotationStatus
    annotator_id: str
    annotator_type: AnnotatorType
    reviews: tuple[ReviewRecord, ...] = ()
    evidence_tags: tuple[EvidenceTag, ...] = ()
    rationale: str | None = None
    manifest_hash: str = ""
    canonical_piece_hash: str = ""
    canonical_schema_version: int = 1
    annotation_schema_version: int = THEME_ANNOTATION_SCHEMA_VERSION
    theme_family_id: str | None = None
    theme_identity_label: str | None = None
    source_start_measure_label: str | None = None
    source_end_measure_label: str | None = None
    start_event_id: str | None = None
    end_event_id_exclusive: str | None = None
    voice_scope_hint: str | None = None

    def __post_init__(self) -> None:
        if not self.annotation_id or not self.annotation_id.strip():
            raise ValueError("ThemeAnnotation.annotation_id cannot be empty.")
        if not self.piece_id or not self.piece_id.strip():
            raise ValueError("ThemeAnnotation.piece_id cannot be empty.")
        if not isinstance(self.span, ThemeSpan):
            raise TypeError(f"ThemeAnnotation.span must be ThemeSpan, got {type(self.span).__name__}.")
        if not isinstance(self.theme_role, ThemeRole):
            raise TypeError(f"Invalid theme_role {self.theme_role!r}.")
        if not isinstance(self.status, AnnotationStatus):
            raise TypeError(f"Invalid status {self.status!r}.")
        if not isinstance(self.annotator_type, AnnotatorType):
            raise TypeError(f"Invalid annotator_type {self.annotator_type!r}.")

        # Confidence validation: strict 1, 2, or 3 integer
        if (
            isinstance(self.confidence, bool)
            or not isinstance(self.confidence, int)
            or self.confidence not in (1, 2, 3)
        ):
            raise ValueError(f"Confidence must be an integer 1, 2, or 3, got {self.confidence!r}.")

        if self.annotation_schema_version != THEME_ANNOTATION_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported annotation_schema_version {self.annotation_schema_version}. "
                f"Expected {THEME_ANNOTATION_SCHEMA_VERSION}."
            )

        # Acceptance policy validation
        if self.status == AnnotationStatus.ACCEPTED:
            if self.confidence < 2:
                raise ValueError(
                    f"Annotation status ACCEPTED requires confidence >= 2, got {self.confidence}."
                )
            approving_reviews = [r for r in self.reviews if r.decision == ReviewDecision.APPROVE]
            if not approving_reviews:
                raise ValueError(
                    "Annotation status ACCEPTED requires at least one approving ReviewRecord (decision == APPROVE)."
                )

        # Hard Rule: Algorithm candidates can never self-accept without independent review
        if self.annotator_type == AnnotatorType.ALGORITHM_CANDIDATE and self.status == AnnotationStatus.ACCEPTED:
            has_human_approval = any(
                r.decision == ReviewDecision.APPROVE
                and r.reviewer_type in (ReviewerType.SECOND_HUMAN_REVIEW, ReviewerType.MUSIC_THEORY_REVIEWER)
                for r in self.reviews
            )
            if not has_human_approval:
                raise ValueError(
                    "ALGORITHM_CANDIDATE proposals cannot have status ACCEPTED without independent human review approval."
                )


@dataclass(frozen=True, slots=True)
class PieceAnnotationRecord:
    """
    Review state record for a canonical piece (including ANNOTATED_NO_CLEAR_THEME outcomes).
    """
    piece_id: str
    corpus_id: str
    score_entry_id: str
    status: PieceReviewStatus
    canonical_piece_hash: str
    notes: str | None = None
    reviewed_at: str | None = None

    def __post_init__(self) -> None:
        if not self.piece_id or not self.piece_id.strip():
            raise ValueError("PieceAnnotationRecord.piece_id cannot be empty.")
        if not isinstance(self.status, PieceReviewStatus):
            raise TypeError(f"Invalid status {self.status!r}.")


def compute_annotation_id(
    piece_id: str,
    span: ThemeSpan,
    theme_role: ThemeRole,
    discriminator: str | None = None,
    schema_version: int = THEME_ANNOTATION_SCHEMA_VERSION,
) -> str:
    """
    Derives a deterministic, collision-resistant annotation ID from canonical coordinates.
    """
    payload = (
        f"{piece_id}:m{span.start.measure_index}+{span.start.offset}"
        f"-m{span.end.measure_index}+{span.end.offset}:{theme_role.value}:v{schema_version}"
    )
    if discriminator:
        payload += f":{discriminator}"
    sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"ann_{piece_id}_{sha}"


def compute_annotation_set_hash(
    annotations: "Sequence[ThemeAnnotation]",
    piece_records: "Sequence[PieceAnnotationRecord]" = (),
) -> str:
    """
    Computes a deterministic 64-character SHA-256 fingerprint of the annotation dataset.
    Excludes volatile edit timestamps, formatting variations, and rationale whitespace.
    """
    sorted_annos = sorted(
        annotations,
        key=lambda a: (
            a.piece_id,
            a.span.start.measure_index,
            a.span.start.offset,
            a.span.end.measure_index,
            a.span.end.offset,
            a.theme_role.value,
            a.annotation_id,
        ),
    )
    sorted_records = sorted(piece_records, key=lambda r: r.piece_id)

    canonical_data: dict[str, Any] = {
        "annotations": [
            {
                "annotation_id": a.annotation_id,
                "piece_id": a.piece_id,
                "corpus_id": a.corpus_id,
                "score_entry_id": a.score_entry_id,
                "span": {
                    "start": {
                        "measure_index": a.span.start.measure_index,
                        "offset": str(a.span.start.offset),
                    },
                    "end": {
                        "measure_index": a.span.end.measure_index,
                        "offset": str(a.span.end.offset),
                    },
                },
                "theme_role": a.theme_role.value,
                "confidence": a.confidence,
                "status": a.status.value,
                "annotator_id": a.annotator_id,
                "annotator_type": a.annotator_type.value,
                "reviews": [
                    {
                        "reviewer_id": r.reviewer_id,
                        "reviewer_type": r.reviewer_type.value,
                        "decision": r.decision.value,
                    }
                    for r in sorted(a.reviews, key=lambda x: (x.reviewer_id, x.decision.value))
                ],
                "evidence_tags": sorted([e.value for e in a.evidence_tags]),
                "canonical_piece_hash": a.canonical_piece_hash,
                "manifest_hash": a.manifest_hash,
                "canonical_schema_version": a.canonical_schema_version,
                "annotation_schema_version": a.annotation_schema_version,
            }
            for a in sorted_annos
        ],
        "piece_records": [
            {
                "piece_id": r.piece_id,
                "status": r.status.value,
                "canonical_piece_hash": r.canonical_piece_hash,
            }
            for r in sorted_records
        ],
    }
    encoded = json.dumps(canonical_data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

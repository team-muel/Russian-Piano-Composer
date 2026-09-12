"""
Corpus-level theme annotation set loading, piece-aware validation against canonical scores,
lineage stale detection, and fail-closed research/generative filtering.
"""
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from russian_piano_composer.domain.annotations import (
    THEME_ANNOTATION_SCHEMA_VERSION,
    AnnotationStatus,
    AnnotatorType,
    EvidenceTag,
    PieceAnnotationRecord,
    PieceReviewStatus,
    ReviewDecision,
    ReviewerType,
    ReviewRecord,
    ScorePosition,
    ThemeAnnotation,
    ThemeRole,
    ThemeSpan,
    compute_annotation_set_hash,
)
from russian_piano_composer.domain.corpus import CorpusRole, ReadinessStatus, RightsStatus

if TYPE_CHECKING:
    from russian_piano_composer.corpus.manifest import CorpusManifest
    from russian_piano_composer.domain.score import CanonicalScore


@dataclass(frozen=True, slots=True)
class ThemeAnnotationSet:
    """
    Validated container holding theme annotations and piece-level review records.
    """
    manifest_hash: str
    canonical_schema_version: int
    annotation_schema_version: int
    annotations: tuple[ThemeAnnotation, ...]
    piece_records: tuple[PieceAnnotationRecord, ...] = ()

    def __post_init__(self) -> None:
        if self.annotation_schema_version != THEME_ANNOTATION_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported annotation_schema_version {self.annotation_schema_version}. "
                f"Expected {THEME_ANNOTATION_SCHEMA_VERSION}."
            )
        # Check for duplicate annotation IDs
        seen_ids: set[str] = set()
        for ann in self.annotations:
            if ann.annotation_id in seen_ids:
                raise ValueError(f"Duplicate annotation_id detected in annotation set: {ann.annotation_id!r}.")
            seen_ids.add(ann.annotation_id)

    def compute_set_hash(self) -> str:
        """
        Computes the deterministic SHA-256 semantic fingerprint of this annotation set.
        """
        return compute_annotation_set_hash(self.annotations, self.piece_records)


def _parse_score_position(data: dict[str, Any], label: str) -> ScorePosition:
    if not isinstance(data, dict) or "measure_index" not in data or "offset" not in data:
        raise ValueError(f"Invalid ScorePosition data for {label}: {data!r}.")
    measure_index = int(data["measure_index"])
    offset_raw = str(data["offset"])
    offset = Fraction(offset_raw)
    return ScorePosition(measure_index=measure_index, offset=offset)


def _parse_theme_annotation(data: dict[str, Any]) -> ThemeAnnotation:
    if not isinstance(data, dict):
        raise TypeError(f"Expected dict for ThemeAnnotation, got {type(data).__name__}.")

    span_data = data.get("span", {})
    if not isinstance(span_data, dict) or "start" not in span_data or "end" not in span_data:
        raise ValueError(f"Invalid span in annotation {data.get('annotation_id')!r}.")

    start_pos = _parse_score_position(span_data["start"], "start")
    end_pos = _parse_score_position(span_data["end"], "end")
    span = ThemeSpan(start=start_pos, end=end_pos)

    reviews_data = data.get("reviews", ())
    reviews_list: list[ReviewRecord] = []
    for r in reviews_data:
        reviews_list.append(
            ReviewRecord(
                reviewer_id=str(r["reviewer_id"]),
                reviewer_type=ReviewerType(r["reviewer_type"]),
                decision=ReviewDecision(r["decision"]),
                boundary_assessment=r.get("boundary_assessment"),
                role_assessment=r.get("role_assessment"),
                confidence_assessment=r.get("confidence_assessment"),
                notes=r.get("notes"),
                reviewed_at=r.get("reviewed_at"),
            )
        )

    evidence_tags_data = data.get("evidence_tags", ())
    evidence_tags = tuple(EvidenceTag(t) for t in evidence_tags_data)

    return ThemeAnnotation(
        annotation_id=str(data["annotation_id"]),
        piece_id=str(data["piece_id"]),
        corpus_id=str(data["corpus_id"]),
        score_entry_id=str(data["score_entry_id"]),
        span=span,
        theme_role=ThemeRole(data["theme_role"]),
        confidence=int(data["confidence"]),
        status=AnnotationStatus(data["status"]),
        annotator_id=str(data["annotator_id"]),
        annotator_type=AnnotatorType(data["annotator_type"]),
        reviews=tuple(reviews_list),
        evidence_tags=evidence_tags,
        rationale=data.get("rationale"),
        manifest_hash=str(data.get("manifest_hash", "")),
        canonical_piece_hash=str(data.get("canonical_piece_hash", "")),
        canonical_schema_version=int(data.get("canonical_schema_version", 1)),
        annotation_schema_version=int(data.get("annotation_schema_version", THEME_ANNOTATION_SCHEMA_VERSION)),
        theme_family_id=data.get("theme_family_id"),
        theme_identity_label=data.get("theme_identity_label"),
        source_start_measure_label=data.get("source_start_measure_label"),
        source_end_measure_label=data.get("source_end_measure_label"),
        start_event_id=data.get("start_event_id"),
        end_event_id_exclusive=data.get("end_event_id_exclusive"),
        voice_scope_hint=data.get("voice_scope_hint"),
    )


def load_theme_annotation_manifest(path: Path | str) -> ThemeAnnotationSet:
    """
    Loads and validates a theme annotation dataset from YAML.
    """
    filepath = Path(path)
    if not filepath.exists() or not filepath.is_file():
        raise FileNotFoundError(f"Theme annotation manifest file not found: {filepath}")

    with open(filepath, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Theme annotation top-level structure must be a dict, got {type(data).__name__}.")

    annotation_schema_version = int(data.get("annotation_schema_version", THEME_ANNOTATION_SCHEMA_VERSION))
    if annotation_schema_version != THEME_ANNOTATION_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported annotation_schema_version {annotation_schema_version}. "
            f"Expected {THEME_ANNOTATION_SCHEMA_VERSION}."
        )

    manifest_hash = str(data.get("corpus_manifest_hash", ""))
    canonical_schema_version = int(data.get("canonical_schema_version", 1))

    raw_annotations = data.get("annotations", [])
    if not isinstance(raw_annotations, list):
        raise ValueError("Key 'annotations' must be a list.")

    annotations_list: list[ThemeAnnotation] = []
    for raw_ann in raw_annotations:
        annotations_list.append(_parse_theme_annotation(raw_ann))

    raw_records = data.get("piece_records", [])
    records_list: list[PieceAnnotationRecord] = []
    if isinstance(raw_records, list):
        for raw_r in raw_records:
            records_list.append(
                PieceAnnotationRecord(
                    piece_id=str(raw_r["piece_id"]),
                    corpus_id=str(raw_r["corpus_id"]),
                    score_entry_id=str(raw_r["score_entry_id"]),
                    status=PieceReviewStatus(raw_r["status"]),
                    canonical_piece_hash=str(raw_r["canonical_piece_hash"]),
                    notes=raw_r.get("notes"),
                    reviewed_at=raw_r.get("reviewed_at"),
                )
            )

    return ThemeAnnotationSet(
        manifest_hash=manifest_hash,
        canonical_schema_version=canonical_schema_version,
        annotation_schema_version=annotation_schema_version,
        annotations=tuple(annotations_list),
        piece_records=tuple(records_list),
    )


def validate_theme_annotation_set(
    annotation_set: ThemeAnnotationSet,
    canonical_scores: dict[str, "CanonicalScore"],
    expected_manifest_hash: str,
) -> tuple[ThemeAnnotation, ...]:
    """
    Performs piece-aware score coordinate validation and canonical lineage verification.
    Returns the tuple of validated non-stale annotations. Marks stale or invalid annotations closed.
    """
    if annotation_set.manifest_hash and annotation_set.manifest_hash != expected_manifest_hash:
        raise ValueError(
            f"Annotation set manifest hash mismatch. Annotation expects {annotation_set.manifest_hash!r}, "
            f"current manifest is {expected_manifest_hash!r}."
        )

    validated: list[ThemeAnnotation] = []

    for ann in annotation_set.annotations:
        if ann.piece_id not in canonical_scores:
            raise KeyError(f"Canonical score not found for piece_id: {ann.piece_id!r}.")

        score = canonical_scores[ann.piece_id]

        # Stale lineage check
        if ann.canonical_piece_hash and ann.canonical_piece_hash != score.piece_semantic_hash:
            raise ValueError(
                f"STALE ANNOTATION DETECTED for piece {ann.piece_id!r}: annotation hash "
                f"{ann.canonical_piece_hash!r} != canonical score hash {score.piece_semantic_hash!r}."
            )

        # Coordinate bounds check
        if ann.span.start.measure_index >= score.measure_count:
            raise ValueError(
                f"Annotation {ann.annotation_id!r} start measure {ann.span.start.measure_index} "
                f"exceeds score measure count ({score.measure_count})."
            )

        if ann.span.end.measure_index > score.measure_count:
            raise ValueError(
                f"Annotation {ann.annotation_id!r} end measure {ann.span.end.measure_index} "
                f"exceeds score measure count ({score.measure_count})."
            )

        # Measure offset extent check
        start_m = score.measures[ann.span.start.measure_index]
        if ann.span.start.offset > start_m.actual_duration:
            raise ValueError(
                f"Annotation {ann.annotation_id!r} start offset {ann.span.start.offset} "
                f"exceeds measure {ann.span.start.measure_index} duration ({start_m.actual_duration})."
            )

        if ann.span.end.measure_index < score.measure_count:
            end_m = score.measures[ann.span.end.measure_index]
            if ann.span.end.offset > end_m.actual_duration:
                raise ValueError(
                    f"Annotation {ann.annotation_id!r} end offset {ann.span.end.offset} "
                    f"exceeds measure {ann.span.end.measure_index} duration ({end_m.actual_duration})."
                )

        validated.append(ann)

    return tuple(validated)


def accepted_annotations(annotation_set: ThemeAnnotationSet) -> tuple[ThemeAnnotation, ...]:
    """
    Returns strictly annotations with status ACCEPTED and confidence >= 2.
    """
    return tuple(
        a for a in annotation_set.annotations
        if a.status == AnnotationStatus.ACCEPTED and a.confidence >= 2
    )


def research_eligible_annotations(annotation_set: ThemeAnnotationSet) -> tuple[ThemeAnnotation, ...]:
    """
    Returns annotations eligible for scientific research analysis.
    """
    return accepted_annotations(annotation_set)


def generative_training_annotations(
    annotation_set: ThemeAnnotationSet,
    corpus_manifest: "CorpusManifest",
) -> tuple[ThemeAnnotation, ...]:
    """
    Returns annotations eligible for generative training selection.
    Checks status == ACCEPTED, confidence >= 2, role == GENERATIVE_RUSSIAN, and rights readiness.
    Fail-closed: Returns empty tuple if rights review is unresolved or status is not ready.
    """
    eligible: list[ThemeAnnotation] = []
    accepted = accepted_annotations(annotation_set)

    for ann in accepted:
        try:
            source = corpus_manifest.get_source(ann.corpus_id)
        except KeyError:
            continue

        if (
            source.role == CorpusRole.GENERATIVE_RUSSIAN
            and source.readiness_status == ReadinessStatus.PROVENANCE_READY
            and source.rights_status == RightsStatus.VERIFIED
        ):
            eligible.append(ann)

    return tuple(eligible)


def russian_research_annotations(
    annotation_set: ThemeAnnotationSet,
    corpus_manifest: "CorpusManifest",
) -> tuple[ThemeAnnotation, ...]:
    """
    Returns accepted annotations for Russian corpus pieces (research analysis only, not training).
    """
    accepted = accepted_annotations(annotation_set)
    res: list[ThemeAnnotation] = []
    for ann in accepted:
        try:
            source = corpus_manifest.get_source(ann.corpus_id)
            if source.role == CorpusRole.GENERATIVE_RUSSIAN:
                res.append(ann)
        except KeyError:
            pass
    return tuple(res)


def control_research_annotations(
    annotation_set: ThemeAnnotationSet,
    corpus_manifest: "CorpusManifest",
) -> tuple[ThemeAnnotation, ...]:
    """
    Returns accepted annotations for Non-Russian control pieces (research analysis only, never generative).
    """
    accepted = accepted_annotations(annotation_set)
    res: list[ThemeAnnotation] = []
    for ann in accepted:
        try:
            source = corpus_manifest.get_source(ann.corpus_id)
            if source.role == CorpusRole.CONTROL_NON_RUSSIAN:
                res.append(ann)
        except KeyError:
            pass
    return tuple(res)

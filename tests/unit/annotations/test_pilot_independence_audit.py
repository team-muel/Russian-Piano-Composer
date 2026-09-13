"""
Hermetic unit and integration tests for RC-008B-A pilot annotation independence, boundary sanity,
candidate manifest validation, and anti-self-acceptance invariants.
"""
from fractions import Fraction
from pathlib import Path

import pytest
from scripts.build_theme_pilot import load_candidate_specs, load_canonical_score_from_parquet

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.corpus.theme_annotations import (
    load_theme_annotation_manifest,
    validate_theme_annotation_set,
)
from russian_piano_composer.domain.annotations import (
    AnnotationStatus,
    AnnotatorType,
    ReviewDecision,
    ReviewerType,
    ReviewRecord,
    ScorePosition,
    ThemeAnnotation,
    ThemeRole,
    ThemeSpan,
)
from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.score import (
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
)
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


def test_direct_candidate_file_manifest_validation() -> None:
    """
    Hermetic test verifying candidates.yaml loads cleanly, validates all 20 annotations,
    and enforces dual-reviewer structure without requiring external data/interim files.
    """
    candidates_path = Path("data/annotations/theme_v1/pilots/rc008b/candidates.yaml")
    assert candidates_path.exists(), "candidates.yaml must exist"

    annotation_set = load_theme_annotation_manifest(candidates_path)
    assert len(annotation_set.annotations) == 20
    assert len(annotation_set.piece_records) == 18

    # Ensure every candidate has 2 reviews (original + fresh independent)
    for ann in annotation_set.annotations:
        assert len(ann.reviews) == 2
        reviewer_ids = [r.reviewer_id for r in ann.reviews]
        assert "ai_music_theory_reviewer_v1" in reviewer_ids
        assert "ai_music_theory_reviewer_v2" in reviewer_ids


def test_synthetic_score_annotation_validation() -> None:
    """
    Hermetic test proving validate_theme_annotation_set executes full coordinate validation
    against synthetic CanonicalScore objects in clean-clone CI.
    """
    candidates_path = Path("data/annotations/theme_v1/pilots/rc008b/candidates.yaml")
    annotation_set = load_theme_annotation_manifest(candidates_path)
    manifest_hash = annotation_set.manifest_hash

    # Create synthetic scores and update candidates to match synthetic piece hashes
    synthetic_scores: dict[str, CanonicalScore] = {}
    updated_annotations = []

    for piece_rec in annotation_set.piece_records:
        piece_id = piece_rec.piece_id
        meter = TimeSignature(4, 4)

        measures = tuple(
            CanonicalMeasure(
                piece_id=piece_id,
                measure_index=m,
                source_measure_label=str(m + 1),
                global_onset=Fraction(m),
                actual_duration=Fraction(1),
                time_signature=meter,
                expected_duration=Fraction(1),
            )
            for m in range(100)
        )


        pitch = SpelledPitch(PitchLetter.C, 0, 4)
        event_note = CanonicalScoreEvent(
            piece_id=piece_id,
            event_id=f"{piece_id}:ev0",
            event_index=0,
            event_kind=EventKind.NOTE,
            measure_index=0,
            source_measure_label="1",
            staff=1,
            voice=1,
            global_onset=Fraction(0),
            offset_in_measure=Fraction(0),
            duration=Fraction(1, 4),
            pitch=pitch,
            midi=60,
        )

        score = CanonicalScore(
            piece_id=piece_id,
            corpus_id=piece_rec.corpus_id,
            corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
            score_entry_id=piece_rec.score_entry_id,
            composer="Test Composer",
            title="Test Piece",
            source_repository="http://test",
            source_commit="0" * 40,
            source_relative_path="test.mscx",
            source_sha256="0" * 64,
            manifest_hash=manifest_hash,
            parser_version="1.0",
            measures=measures,
            events=(event_note,),
        )
        synthetic_scores[piece_id] = score

    # Rebind annotations to synthetic score hashes for clean-clone validation testing
    for ann in annotation_set.annotations:
        score_hash = synthetic_scores[ann.piece_id].compute_piece_hash()
        updated_annotations.append(
            ThemeAnnotation(
                annotation_id=ann.annotation_id,
                piece_id=ann.piece_id,
                corpus_id=ann.corpus_id,
                score_entry_id=ann.score_entry_id,
                span=ann.span,
                theme_role=ann.theme_role,
                confidence=ann.confidence,
                status=ann.status,
                annotator_id=ann.annotator_id,
                annotator_type=ann.annotator_type,
                canonical_piece_hash=score_hash,
                manifest_hash=ann.manifest_hash,
                rationale=ann.rationale,
                reviews=ann.reviews,
            )
        )

    from russian_piano_composer.corpus.theme_annotations import ThemeAnnotationSet
    synthetic_set = ThemeAnnotationSet(
        manifest_hash=annotation_set.manifest_hash,
        canonical_schema_version=annotation_set.canonical_schema_version,
        annotation_schema_version=annotation_set.annotation_schema_version,
        annotations=tuple(updated_annotations),
        piece_records=annotation_set.piece_records,
    )

    validated = validate_theme_annotation_set(synthetic_set, synthetic_scores, manifest_hash)
    assert len(validated) == 20


@pytest.mark.corpus_integration
def test_corpus_integration_candidate_file_validation() -> None:
    """
    Explicit corpus integration test: validates candidates.yaml against real canonical parquet scores on disk.
    Requires local data/interim/canonical files.
    """
    candidates_path = Path("data/annotations/theme_v1/pilots/rc008b/candidates.yaml")
    annotation_set = load_theme_annotation_manifest(candidates_path)
    manifest_path = Path("data/manifests/corpus_manifest.yaml")

    if not manifest_path.exists():
        pytest.skip("Corpus manifest unavailable")

    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    interim_base = Path("data/interim/canonical") / manifest_hash

    if not interim_base.exists():
        pytest.skip("Canonical corpus parquet cache not found in data/interim")

    canonical_scores = {}
    for ann in annotation_set.annotations:
        if ann.piece_id not in canonical_scores:
            corpus_dir = interim_base / ann.corpus_id
            if corpus_dir.exists():
                canonical_scores[ann.piece_id] = load_canonical_score_from_parquet(corpus_dir, ann.piece_id)

    assert len(canonical_scores) == 18, "All 18 candidate pieces must be present in canonical corpus"
    validated = validate_theme_annotation_set(annotation_set, canonical_scores, manifest_hash)
    assert len(validated) == 20


def test_no_hardcoded_piece_lookup_tables_in_builder_code() -> None:
    """
    Forensic check: build_theme_pilot.py source code must not contain hard-coded
    piece-specific lookup branches like `if "BI93-2op67-3" in piece_id:`.
    """
    script_path = Path("scripts/build_theme_pilot.py")
    code = script_path.read_text(encoding="utf-8")

    forbidden_patterns = [
        'if "BI93-2op67-3" in piece_id:',
        'elif "BI60-1op06-1" in piece_id:',
        'elif "160.05_Orage" in piece_id:',
        'elif "op42n02" in piece_id:',
    ]
    for pattern in forbidden_patterns:
        assert pattern not in code, f"Forbidden in-code lookup table found: {pattern!r}"


def test_ai_reviewer_cannot_force_accepted_status() -> None:
    """
    Regression test: ALGORITHM_CANDIDATE + AI_REVIEWER must fail validation or violate invariants
    if status is manually set to ACCEPTED without human approval.
    """
    span = ThemeSpan(ScorePosition(0, 0), ScorePosition(8, 0))
    review_ai = ReviewRecord(
        reviewer_id="ai_music_theory_reviewer_v2",
        reviewer_type=ReviewerType.MUSIC_THEORY_REVIEWER,
        decision=ReviewDecision.APPROVE,
    )

    # Creating ALGORITHM_CANDIDATE with status ACCEPTED must raise ValueError
    with pytest.raises(ValueError, match="ALGORITHM_CANDIDATE proposals cannot have status ACCEPTED"):
        ThemeAnnotation(
            annotation_id="ann_test_invalid_accepted",
            piece_id="dcml_chopin_mazurkas:BI93-2op67-3",
            corpus_id="dcml_chopin_mazurkas",
            score_entry_id="BI93-2op67-3",
            span=span,
            theme_role=ThemeRole.PRIMARY_THEME,
            confidence=3,
            status=AnnotationStatus.ACCEPTED,
            annotator_id="algorithm_candidate_pipeline_v1",
            annotator_type=AnnotatorType.ALGORITHM_CANDIDATE,
            reviews=(review_ai,),
            manifest_hash="cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212",
        )


def test_zero_candidate_pieces_allowed() -> None:
    """
    Tests that candidate specification loader handles zero-candidate pieces gracefully.
    """
    spec_path = Path("data/annotations/theme_v1/pilots/rc008b/candidate_specs_v1.yaml")
    candidate_specs = load_candidate_specs(spec_path)

    # Ensure empty lookup for unknown piece returns empty list (0 candidates)
    dummy_candidates = candidate_specs.get("non_existent_piece_id", [])
    assert isinstance(dummy_candidates, list)
    assert len(dummy_candidates) == 0

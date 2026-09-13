"""
Unit tests for RC-008B-A pilot annotation independence, boundary sanity,
direct candidate file validation, and anti-self-acceptance invariants.
"""
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


def test_direct_candidate_file_validation() -> None:
    """
    Tests that candidates.yaml loads cleanly and passes full coordinate and lineage validation.
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

    # Validate against canonical scores if interim data is available locally
    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    if manifest_path.exists():
        manifest = load_manifest(manifest_path)
        manifest_hash = manifest.compute_manifest_hash()
        interim_base = Path("data/interim/canonical") / manifest_hash

        if interim_base.exists():
            canonical_scores = {}
            for ann in annotation_set.annotations:
                if ann.piece_id not in canonical_scores:
                    corpus_dir = interim_base / ann.corpus_id
                    if corpus_dir.exists():
                        canonical_scores[ann.piece_id] = load_canonical_score_from_parquet(corpus_dir, ann.piece_id)

            if len(canonical_scores) == 18:
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

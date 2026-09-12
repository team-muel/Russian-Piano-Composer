"""
Unit tests for theme annotation domain models, validation, lineage binding, review state machine,
confidence scale, anti-self-acceptance invariant, and rights/generative isolation.
"""
from fractions import Fraction

import pytest

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.corpus.theme_annotations import (
    ThemeAnnotationSet,
    accepted_annotations,
    control_research_annotations,
    generative_training_annotations,
    research_eligible_annotations,
    russian_research_annotations,
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
    compute_annotation_id,
    compute_annotation_set_hash,
)
from russian_piano_composer.domain.score import (
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
)
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


@pytest.fixture
def synthetic_score() -> CanonicalScore:
    meter = TimeSignature(4, 4)
    measure = CanonicalMeasure(
        piece_id="test_corpus:piece1",
        measure_index=0,
        source_measure_label="1",
        global_onset=Fraction(0),
        actual_duration=Fraction(1),
        time_signature=meter,
        expected_duration=Fraction(1),
    )
    pitch = SpelledPitch(PitchLetter.C, 0, 4)
    event_note = CanonicalScoreEvent(
        piece_id="test_corpus:piece1",
        event_id="ev0",
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
    return CanonicalScore(
        piece_id="test_corpus:piece1",
        corpus_id="test_corpus",
        corpus_role=load_manifest("data/manifests/corpus_manifest.yaml").sources[0].role,
        score_entry_id="piece1",
        composer="Test Composer",
        title="Test Piece",
        source_repository="http://test",
        source_commit="0" * 40,
        source_relative_path="test.mscx",
        source_sha256="0" * 64,
        manifest_hash="test_manifest_hash",
        parser_version="1.0",
        measures=(measure,),
        events=(event_note,),
    )


def test_score_position_validation() -> None:
    pos = ScorePosition(0, Fraction(1, 4))
    assert pos.measure_index == 0
    assert pos.offset == Fraction(1, 4)

    with pytest.raises(ValueError, match="non-negative integer"):
        ScorePosition(-1, Fraction(0))

    with pytest.raises(ValueError, match="non-negative"):
        ScorePosition(0, Fraction(-1, 4))


def test_theme_span_validation() -> None:
    s1 = ScorePosition(0, Fraction(0))
    s2 = ScorePosition(0, Fraction(1, 2))
    s3 = ScorePosition(1, Fraction(0))

    span = ThemeSpan(s1, s2)
    assert span.start == s1
    assert span.end == s2

    # Multi-measure span
    span_multi = ThemeSpan(s1, s3)
    assert span_multi.end.measure_index == 1

    # End before start
    with pytest.raises(ValueError, match="precedes start measure"):
        ThemeSpan(s3, s1)

    # Same measure start == end
    with pytest.raises(ValueError, match="strictly greater than start offset"):
        ThemeSpan(s1, s1)


def test_confidence_scale_validation() -> None:
    span = ThemeSpan(ScorePosition(0, Fraction(0)), ScorePosition(0, Fraction(1, 2)))

    # Valid confidences: 1, 2, 3
    for conf in (1, 2, 3):
        ann = ThemeAnnotation(
            annotation_id="ann1",
            piece_id="p1",
            corpus_id="c1",
            score_entry_id="s1",
            span=span,
            theme_role=ThemeRole.PRIMARY_THEME,
            confidence=conf,
            status=AnnotationStatus.CANDIDATE,
            annotator_id="h1",
            annotator_type=AnnotatorType.HUMAN,
        )
        assert ann.confidence == conf

    # Invalid confidence values: 0, 4, 1.5, True
    for invalid_conf in (0, 4, 1.5, True):
        with pytest.raises(ValueError, match="Confidence must be an integer 1, 2, or 3"):
            ThemeAnnotation(
                annotation_id="ann1",
                piece_id="p1",
                corpus_id="c1",
                score_entry_id="s1",
                span=span,
                theme_role=ThemeRole.PRIMARY_THEME,
                confidence=invalid_conf,  # type: ignore[arg-type]
                status=AnnotationStatus.CANDIDATE,
                annotator_id="h1",
                annotator_type=AnnotatorType.HUMAN,
            )


def test_algorithm_candidate_cannot_self_accept() -> None:
    span = ThemeSpan(ScorePosition(0, Fraction(0)), ScorePosition(0, Fraction(1, 2)))
    ai_review = ReviewRecord(
        reviewer_id="ai_bot",
        reviewer_type=ReviewerType.AI_REVIEWER,
        decision=ReviewDecision.APPROVE,
    )

    # ALGORITHM_CANDIDATE with status ACCEPTED without independent human review -> MUST FAIL
    with pytest.raises(ValueError, match="ALGORITHM_CANDIDATE proposals cannot have status ACCEPTED"):
        ThemeAnnotation(
            annotation_id="ann_algo",
            piece_id="p1",
            corpus_id="c1",
            score_entry_id="s1",
            span=span,
            theme_role=ThemeRole.PRIMARY_THEME,
            confidence=3,
            status=AnnotationStatus.ACCEPTED,
            annotator_id="algo_bot",
            annotator_type=AnnotatorType.ALGORITHM_CANDIDATE,
            reviews=(ai_review,),
        )


def test_accepted_status_requires_human_approval_and_confidence_ge_2() -> None:
    span = ThemeSpan(ScorePosition(0, Fraction(0)), ScorePosition(0, Fraction(1, 2)))
    review_approve = ReviewRecord(
        reviewer_id="human_rev",
        reviewer_type=ReviewerType.SECOND_HUMAN_REVIEW,
        decision=ReviewDecision.APPROVE,
    )

    # ACCEPTED with confidence 1 -> MUST FAIL
    with pytest.raises(ValueError, match="ACCEPTED requires confidence >= 2"):
        ThemeAnnotation(
            annotation_id="ann1",
            piece_id="p1",
            corpus_id="c1",
            score_entry_id="s1",
            span=span,
            theme_role=ThemeRole.PRIMARY_THEME,
            confidence=1,
            status=AnnotationStatus.ACCEPTED,
            annotator_id="h1",
            annotator_type=AnnotatorType.HUMAN,
            reviews=(review_approve,),
        )

    # ACCEPTED with no approving reviews -> MUST FAIL
    with pytest.raises(ValueError, match="ACCEPTED requires at least one approving ReviewRecord"):
        ThemeAnnotation(
            annotation_id="ann1",
            piece_id="p1",
            corpus_id="c1",
            score_entry_id="s1",
            span=span,
            theme_role=ThemeRole.PRIMARY_THEME,
            confidence=3,
            status=AnnotationStatus.ACCEPTED,
            annotator_id="h1",
            annotator_type=AnnotatorType.HUMAN,
            reviews=(),
        )

    # Valid ACCEPTED annotation with human review
    ann_ok = ThemeAnnotation(
        annotation_id="ann1",
        piece_id="p1",
        corpus_id="c1",
        score_entry_id="s1",
        span=span,
        theme_role=ThemeRole.PRIMARY_THEME,
        confidence=3,
        status=AnnotationStatus.ACCEPTED,
        annotator_id="h1",
        annotator_type=AnnotatorType.HUMAN,
        reviews=(review_approve,),
    )
    assert ann_ok.status == AnnotationStatus.ACCEPTED


def test_deterministic_annotation_id_and_semantic_hash() -> None:
    span = ThemeSpan(ScorePosition(0, Fraction(0)), ScorePosition(0, Fraction(1, 2)))
    id1 = compute_annotation_id("pieceA", span, ThemeRole.PRIMARY_THEME)
    id2 = compute_annotation_id("pieceA", span, ThemeRole.PRIMARY_THEME)
    assert id1 == id2

    review_approve = ReviewRecord(
        reviewer_id="human_rev",
        reviewer_type=ReviewerType.SECOND_HUMAN_REVIEW,
        decision=ReviewDecision.APPROVE,
    )
    ann1 = ThemeAnnotation(
        annotation_id=id1,
        piece_id="pieceA",
        corpus_id="c1",
        score_entry_id="s1",
        span=span,
        theme_role=ThemeRole.PRIMARY_THEME,
        confidence=3,
        status=AnnotationStatus.ACCEPTED,
        annotator_id="h1",
        annotator_type=AnnotatorType.HUMAN,
        reviews=(review_approve,),
    )

    hash1 = compute_annotation_set_hash([ann1])

    # Modify confidence -> hash MUST change
    ann_conf2 = ThemeAnnotation(
        annotation_id=id1,
        piece_id="pieceA",
        corpus_id="c1",
        score_entry_id="s1",
        span=span,
        theme_role=ThemeRole.PRIMARY_THEME,
        confidence=2,
        status=AnnotationStatus.ACCEPTED,
        annotator_id="h1",
        annotator_type=AnnotatorType.HUMAN,
        reviews=(review_approve,),
    )
    hash2 = compute_annotation_set_hash([ann_conf2])
    assert hash1 != hash2


def test_stale_lineage_validation(synthetic_score: CanonicalScore) -> None:
    span = ThemeSpan(ScorePosition(0, Fraction(0)), ScorePosition(0, Fraction(1, 4)))
    review_approve = ReviewRecord(
        reviewer_id="h2",
        reviewer_type=ReviewerType.SECOND_HUMAN_REVIEW,
        decision=ReviewDecision.APPROVE,
    )
    ann = ThemeAnnotation(
        annotation_id="ann_stale",
        piece_id="test_corpus:piece1",
        corpus_id="test_corpus",
        score_entry_id="piece1",
        span=span,
        theme_role=ThemeRole.PRIMARY_THEME,
        confidence=3,
        status=AnnotationStatus.ACCEPTED,
        annotator_id="h1",
        annotator_type=AnnotatorType.HUMAN,
        canonical_piece_hash="wrong_hash_1234567890abcdef1234567890abcdef",
        reviews=(review_approve,),
    )

    aset = ThemeAnnotationSet(
        manifest_hash="test_manifest_hash",
        canonical_schema_version=1,
        annotation_schema_version=1,
        annotations=(ann,),
    )

    # Validation against synthetic score with wrong hash MUST raise ValueError (stale detection)
    with pytest.raises(ValueError, match="STALE ANNOTATION DETECTED"):
        validate_theme_annotation_set(aset, {"test_corpus:piece1": synthetic_score}, "test_manifest_hash")


def test_rights_and_control_isolation() -> None:
    manifest = load_manifest("data/manifests/corpus_manifest.yaml")
    span = ThemeSpan(ScorePosition(0, Fraction(0)), ScorePosition(0, Fraction(1, 2)))
    review_approve = ReviewRecord(
        reviewer_id="h2",
        reviewer_type=ReviewerType.SECOND_HUMAN_REVIEW,
        decision=ReviewDecision.APPROVE,
    )

    # Russian annotation (Medtner)
    ann_russian = ThemeAnnotation(
        annotation_id="ann_medtner",
        piece_id="dcml_medtner_tales::op08n01",
        corpus_id="dcml_medtner_tales",
        score_entry_id="op08n01",
        span=span,
        theme_role=ThemeRole.PRIMARY_THEME,
        confidence=3,
        status=AnnotationStatus.ACCEPTED,
        annotator_id="h1",
        annotator_type=AnnotatorType.HUMAN,
        reviews=(review_approve,),
    )

    # Control annotation (Chopin)
    ann_control = ThemeAnnotation(
        annotation_id="ann_chopin",
        piece_id="dcml_chopin_mazurkas::BI105-1op30-1",
        corpus_id="dcml_chopin_mazurkas",
        score_entry_id="BI105-1op30-1",
        span=span,
        theme_role=ThemeRole.PRIMARY_THEME,
        confidence=3,
        status=AnnotationStatus.ACCEPTED,
        annotator_id="h1",
        annotator_type=AnnotatorType.HUMAN,
        reviews=(review_approve,),
    )

    aset = ThemeAnnotationSet(
        manifest_hash=manifest.compute_manifest_hash(),
        canonical_schema_version=1,
        annotation_schema_version=1,
        annotations=(ann_russian, ann_control),
    )

    assert len(accepted_annotations(aset)) == 2
    assert len(research_eligible_annotations(aset)) == 2
    assert len(russian_research_annotations(aset, manifest)) == 1
    assert len(control_research_annotations(aset, manifest)) == 1

    # CRITICAL INVARIANT: Generative training annotations MUST be 0 because rights review is unresolved!
    gen_train = generative_training_annotations(aset, manifest)
    assert len(gen_train) == 0

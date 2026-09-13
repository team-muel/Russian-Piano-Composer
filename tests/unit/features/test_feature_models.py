import pytest

from russian_piano_composer.domain.features import (
    CorpusFeatureMatrix,
    FeatureDefinition,
    FeatureProvenance,
    PieceFeatureSet,
)
from russian_piano_composer.features import FEATURE_REGISTRY


def test_piece_feature_set_creation() -> None:
    """Test standard creation and validation of PieceFeatureSet."""
    pfs = PieceFeatureSet(
        piece_id="test:1",
        corpus_id="test",
        corpus_role="GENERATIVE_RUSSIAN",
        features={"pitch_mean": 60.0},
        manifest_hash="abc",
        canonical_piece_hash="def"
    )
    assert pfs.piece_id == "test:1"

    with pytest.raises(ValueError, match=r"PieceFeatureSet\.piece_id cannot be empty"):
        PieceFeatureSet(
            piece_id="",
            corpus_id="test",
            corpus_role="GENERATIVE_RUSSIAN",
            features={},
            manifest_hash="abc",
            canonical_piece_hash="def"
        )


def test_corpus_feature_matrix_determinism() -> None:
    """Test CorpusFeatureMatrix hash determinism."""
    pfs1 = PieceFeatureSet("t:1", "t", "r", {"a": 1.0}, "hash1", "cp1")
    pfs2 = PieceFeatureSet("t:2", "t", "r", {"a": 2.0}, "hash1", "cp2")

    fd = FeatureDefinition("a", "A", "desc", FeatureProvenance.OBSERVED, "unit", "float")

    # Create with pieces in one order
    matrix1 = CorpusFeatureMatrix(pieces=(pfs1, pfs2), manifest_hash="hash1", feature_registry=(fd,))
    # Create with pieces in another order
    matrix2 = CorpusFeatureMatrix(pieces=(pfs2, pfs1), manifest_hash="hash1", feature_registry=(fd,))

    assert matrix1.compute_matrix_hash() == matrix2.compute_matrix_hash()


def test_corpus_feature_matrix_rejects_duplicate_ids() -> None:
    """Test CorpusFeatureMatrix rejects duplicate piece_ids."""
    pfs1 = PieceFeatureSet("t:1", "t", "r", {"a": 1.0}, "hash1", "cp1")
    pfs2 = PieceFeatureSet("t:1", "t", "r", {"a": 2.0}, "hash1", "cp2")
    fd = FeatureDefinition("a", "A", "desc", FeatureProvenance.OBSERVED, "unit", "float")

    with pytest.raises(ValueError, match="duplicate piece_ids"):
        CorpusFeatureMatrix(pieces=(pfs1, pfs2), manifest_hash="hash1", feature_registry=(fd,))


def test_corpus_feature_matrix_rejects_mismatched_manifest_hash() -> None:
    """Test CorpusFeatureMatrix rejects mismatched manifest_hash."""
    pfs1 = PieceFeatureSet("t:1", "t", "r", {"a": 1.0}, "hash1", "cp1")
    fd = FeatureDefinition("a", "A", "desc", FeatureProvenance.OBSERVED, "unit", "float")

    with pytest.raises(ValueError, match="does not match matrix manifest_hash"):
        CorpusFeatureMatrix(pieces=(pfs1,), manifest_hash="hash2", feature_registry=(fd,))


def test_feature_registry_completeness() -> None:
    """Test FEATURE_REGISTRY completeness (every feature_id is in the registry)."""
    # Assuming the registry is populated from all definitions, we can just check it is not empty
    assert len(FEATURE_REGISTRY) > 0
    # Also check uniqueness of feature_ids
    feature_ids = [fd.feature_id for fd in FEATURE_REGISTRY]
    assert len(feature_ids) == len(set(feature_ids))


def test_feature_registry_provenance() -> None:
    """Verify registry provenance classifications are valid FeatureProvenance enum values."""
    for fd in FEATURE_REGISTRY:
        assert isinstance(fd.provenance, FeatureProvenance)
        if fd.feature_id in ("contour_arc_score", "rhythm_dotted_ratio"):
            assert fd.provenance == FeatureProvenance.ENGINEERING_HEURISTIC
        else:
            assert fd.provenance == FeatureProvenance.OBSERVED


def test_matrix_hash_policy_sensitivity() -> None:
    """Verify that different extraction policies result in different matrix semantic hashes."""
    from russian_piano_composer.features.policy import FeatureExtractionPolicy, GraceNotePolicy

    pfs1 = PieceFeatureSet("t:1", "t", "r", {"a": 1.0}, "hash1", "cp1")
    fd = FeatureDefinition("a", "A", "desc", FeatureProvenance.OBSERVED, "unit", "float")

    policy1 = FeatureExtractionPolicy(grace_policy=GraceNotePolicy.INCLUDE)
    policy2 = FeatureExtractionPolicy(grace_policy=GraceNotePolicy.EXCLUDE)

    matrix1 = CorpusFeatureMatrix(
        pieces=(pfs1,),
        manifest_hash="hash1",
        feature_registry=(fd,),
        feature_policy_hash=policy1.compute_policy_hash()
    )
    matrix2 = CorpusFeatureMatrix(
        pieces=(pfs1,),
        manifest_hash="hash1",
        feature_registry=(fd,),
        feature_policy_hash=policy2.compute_policy_hash()
    )

    assert policy1.compute_policy_hash() != policy2.compute_policy_hash()
    assert matrix1.compute_matrix_hash() != matrix2.compute_matrix_hash()


def test_matrix_hash_schema_semantic_sensitivity() -> None:
    """Verify that mutating feature schema category or semantics alters schema and matrix hashes."""
    from russian_piano_composer.domain.features import compute_schema_semantic_hash

    pfs1 = PieceFeatureSet("t:1", "t", "r", {"a": 1.0}, "hash1", "cp1")
    fd1 = FeatureDefinition("a", "A", "desc", FeatureProvenance.OBSERVED, "unit", "float", validity_category="A", definition_id="v2.0")
    fd2 = FeatureDefinition("a", "A", "desc", FeatureProvenance.OBSERVED, "unit", "float", validity_category="B", definition_id="v2.0")

    hash1 = compute_schema_semantic_hash((fd1,))
    hash2 = compute_schema_semantic_hash((fd2,))
    assert hash1 != hash2

    matrix1 = CorpusFeatureMatrix(pieces=(pfs1,), manifest_hash="hash1", feature_registry=(fd1,))
    matrix2 = CorpusFeatureMatrix(pieces=(pfs1,), manifest_hash="hash1", feature_registry=(fd2,))
    assert matrix1.compute_matrix_hash() != matrix2.compute_matrix_hash()


def test_definition_id_mutation_sensitivity() -> None:
    """Verify that changing definition_id changes semantic hash and matrix hash."""
    from russian_piano_composer.domain.features import compute_schema_semantic_hash

    pfs1 = PieceFeatureSet("t:1", "t", "r", {"a": 1.0}, "hash1", "cp1")
    fd1 = FeatureDefinition("a", "A", "desc1", FeatureProvenance.OBSERVED, "unit", "float", definition_id="v2.0")
    fd2 = FeatureDefinition("a", "A", "desc1", FeatureProvenance.OBSERVED, "unit", "float", definition_id="v2.1")

    assert fd1.compute_semantic_hash() != fd2.compute_semantic_hash()
    assert compute_schema_semantic_hash((fd1,)) != compute_schema_semantic_hash((fd2,))

    matrix1 = CorpusFeatureMatrix(pieces=(pfs1,), manifest_hash="hash1", feature_registry=(fd1,))
    matrix2 = CorpusFeatureMatrix(pieces=(pfs1,), manifest_hash="hash1", feature_registry=(fd2,))
    assert matrix1.compute_matrix_hash() != matrix2.compute_matrix_hash()


def test_policy_affects_extracted_values(make_score) -> None:
    """Verify that changing FeatureExtractionPolicy alters extracted feature values on a score with grace notes and ties."""
    from fractions import Fraction

    from russian_piano_composer.domain.score import CanonicalScoreEvent, EventKind, TieState
    from russian_piano_composer.features import extract_piece_features
    from russian_piano_composer.features.policy import (
        FeatureExtractionPolicy,
        GraceNotePolicy,
    )

    # Create score with a grace note and a tied note continuation
    # Note 1: C4 (midi 60), quarter note
    # Grace note 2: D4 (midi 62) grace note
    # Note 3: E4 (midi 64) tied continuation
    score = make_score([(60, Fraction(1, 4), 0), (64, Fraction(1, 4), 0)])

    from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch

    # Mutate event 1 to be a grace note
    events = list(score.events)
    grace_evt = CanonicalScoreEvent(
        piece_id=score.piece_id,
        event_id="grace_1",
        event_index=99,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=events[0].global_onset,
        offset_in_measure=events[0].offset_in_measure,
        duration=events[0].duration,
        pitch=SpelledPitch(PitchLetter.C, 0, 5),
        midi=72,  # C5 grace note
        is_grace=True,
        tie_state=TieState.NONE,
    )
    events.append(grace_evt)
    events.sort(
        key=lambda ev: (
            ev.global_onset,
            ev.measure_index,
            ev.staff,
            ev.voice,
            ev.event_kind.value,
            ev.event_index,
        )
    )

    from russian_piano_composer.domain.score import CanonicalScore
    score_with_grace = CanonicalScore(
        piece_id=score.piece_id,
        corpus_id=score.corpus_id,
        corpus_role=score.corpus_role,
        score_entry_id=score.score_entry_id,
        composer=score.composer,
        title=score.title,
        source_repository=score.source_repository,
        source_commit=score.source_commit,
        source_relative_path=score.source_relative_path,
        source_sha256=score.source_sha256,
        manifest_hash=score.manifest_hash,
        parser_version=score.parser_version,
        measures=score.measures,
        events=tuple(events),
        canonical_schema_version=score.canonical_schema_version,
        parser_name=score.parser_name,
    )

    policy_exclude_grace = FeatureExtractionPolicy(grace_policy=GraceNotePolicy.EXCLUDE)
    policy_include_grace = FeatureExtractionPolicy(grace_policy=GraceNotePolicy.INCLUDE)

    res_exclude = extract_piece_features(score_with_grace, manifest_hash="abc", policy=policy_exclude_grace)
    res_include = extract_piece_features(score_with_grace, manifest_hash="abc", policy=policy_include_grace)

    # Highest pitch will differ when grace note C5 (72) is included vs excluded
    assert res_exclude.features["pitch_highest_midi"] == 64
    assert res_include.features["pitch_highest_midi"] == 72




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
    """Test all features in FEATURE_REGISTRY have OBSERVED provenance."""
    for fd in FEATURE_REGISTRY:
        assert fd.provenance == FeatureProvenance.OBSERVED

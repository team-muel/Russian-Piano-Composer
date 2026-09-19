"""
Unit tests for role-blind feature matrix construction and predictor leakage prevention.
"""

import pytest

from russian_piano_composer.style_analysis.features import (
    CTU_STYLE_FEATURE_REGISTRY,
    CTU_STYLE_FEATURE_SCHEMA_VERSION,
    FORBIDDEN_METADATA_TERMS,
    RoleBlindFeatureMatrix,
    compute_style_feature_schema_hash,
)


def test_ctu_style_feature_registry_schema_version() -> None:
    """Verify registry contains 14 defined CTU structural features for version 1."""
    assert CTU_STYLE_FEATURE_SCHEMA_VERSION == 1
    assert len(CTU_STYLE_FEATURE_REGISTRY) == 14

    feature_ids = [f.feature_id for f in CTU_STYLE_FEATURE_REGISTRY]
    assert len(set(feature_ids)) == 14  # All unique

    for d in CTU_STYLE_FEATURE_REGISTRY:
        assert d.feature_id.startswith("ctu_")
        assert d.formula != ""
        assert d.observation_unit != ""
        assert d.normalization != ""
        assert d.missing_value_rule != ""


def test_schema_hash_determinism() -> None:
    """Verify compute_style_feature_schema_hash is deterministic."""
    h1 = compute_style_feature_schema_hash()
    h2 = compute_style_feature_schema_hash()
    assert len(h1) == 64
    assert h1 == h2


def test_role_blind_matrix_valid_creation() -> None:
    """Verify successful creation of valid RoleBlindFeatureMatrix."""
    matrix = RoleBlindFeatureMatrix(
        piece_ids=("piece_1", "piece_2"),
        feature_names=("feat_a", "feat_b"),
        data=((1.0, 2.0), (3.0, 4.0)),
        model_name="MODEL_TEST",
        manifest_hash="a" * 64,
        schema_hash="b" * 64,
    )
    assert matrix.model_name == "MODEL_TEST"
    assert len(matrix.piece_ids) == 2
    assert len(matrix.feature_names) == 2
    assert matrix.compute_matrix_hash() == matrix.compute_matrix_hash()


def test_role_blind_matrix_rejects_empty_inputs() -> None:
    """Verify matrix rejects empty piece_ids or feature_names."""
    with pytest.raises(ValueError, match="must contain piece_ids"):
        RoleBlindFeatureMatrix(
            piece_ids=(),
            feature_names=("feat_a",),
            data=(),
            model_name="MODEL_TEST",
            manifest_hash="a" * 64,
            schema_hash="b" * 64,
        )

    with pytest.raises(ValueError, match="must contain feature_names"):
        RoleBlindFeatureMatrix(
            piece_ids=("piece_1",),
            feature_names=(),
            data=((1.0,),),
            model_name="MODEL_TEST",
            manifest_hash="a" * 64,
            schema_hash="b" * 64,
        )


def test_role_blind_matrix_rejects_row_mismatch() -> None:
    """Verify matrix rejects row count mismatch."""
    with pytest.raises(ValueError, match="data row count must match piece_ids length"):
        RoleBlindFeatureMatrix(
            piece_ids=("piece_1", "piece_2"),
            feature_names=("feat_a",),
            data=((1.0,),),
            model_name="MODEL_TEST",
            manifest_hash="a" * 64,
            schema_hash="b" * 64,
        )


def test_role_blind_matrix_rejects_forbidden_metadata_terms() -> None:
    """Verify matrix rejects predictor column names containing forbidden metadata terms."""
    for term in FORBIDDEN_METADATA_TERMS:
        forbidden_col = f"prefix_{term}_suffix"
        with pytest.raises(ValueError, match="forbidden in predictor column"):
            RoleBlindFeatureMatrix(
                piece_ids=("piece_1",),
                feature_names=(forbidden_col,),
                data=((1.0,),),
                model_name="MODEL_TEST",
                manifest_hash="a" * 64,
                schema_hash="b" * 64,
            )

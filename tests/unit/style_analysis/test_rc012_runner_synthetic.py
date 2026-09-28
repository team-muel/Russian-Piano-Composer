"""
Unit tests for RC-012 Confirmatory Runner statistical algorithms using synthetic fixtures.
Validates pure algorithmic correctness without exposing real confirmatory data.
"""

from __future__ import annotations

import numpy as np
from scripts.run_rc012_one_shot_confirmation import (
    EXPECTED_RUSSIAN_COMPOSERS,
    compute_piece_ledger_sha256,
    compute_replicate_matrix_sha256,
    run_confirmatory_pipeline,
)


def test_synthetic_confirmatory_pipeline_execution() -> None:
    # Build synthetic 56-feature predictor bundle
    rng = np.random.RandomState(123)
    feature_names = [f"feat_{i}" for i in range(56)]
    mean = rng.normal(0, 1, size=56).tolist()
    scale = rng.uniform(0.5, 2.0, size=56).tolist()
    coefficients = rng.normal(0, 0.5, size=56).tolist()
    intercept = 0.1

    bundle_data = {
        "feature_names": feature_names,
        "scaler": {"mean": mean, "scale": scale},
        "coefficients": coefficients,
        "intercept": intercept,
    }

    # Build synthetic 483-piece cache with 9 composers
    cached_pieces = []
    # 4 Russian composers: 207, 18, 11, 10
    # 5 Control composers: 66, 54, 91, 14, 12
    russian_counts = {
        "Alexander Scriabin": 207,
        "Modest Mussorgsky": 18,
        "Anton Rubinstein": 11,
        "Sergei Prokofiev": 10,
    }
    control_counts = {
        "Edvard Grieg": 66,
        "Claude Debussy": 54,
        "Ludwig van Beethoven": 91,
        "Béla Bartók": 14,
        "Antonín Dvořák": 12,
    }

    piece_idx = 0
    for composer, count in {**russian_counts, **control_counts}.items():
        is_ru = composer in EXPECTED_RUSSIAN_COMPOSERS
        for k in range(count):
            piece_id = f"synth_{composer[:4]}_{k:03d}"
            feat_dict = {f"feat_{i}": float(rng.normal(0.5 if is_ru else -0.5, 1.0)) for i in range(56)}
            cached_pieces.append({
                "piece_id": piece_id,
                "composer": composer,
                "features_56": feat_dict,
            })
            piece_idx += 1

    assert len(cached_pieces) == 483

    cache_data = {"cached_pieces": cached_pieces}

    result_data, _receipt_data, boot_matrix = run_confirmatory_pipeline(
        cache_data=cache_data,
        bundle_data=bundle_data,
        runner_commit_sha="SYNTHETIC_TEST_COMMIT",
    )

    # Verify basic shapes and invariants
    assert len(result_data["piece_score_ledger"]) == 483
    assert len(result_data["composer_level_scores"]) == 9
    assert result_data["primary_hypothesis_result"]["permutation_count"] == 126
    assert 0.0 <= result_data["primary_hypothesis_result"]["p_exact"] <= 1.0
    assert boot_matrix.shape == (10000, 3)

    # Verify hashing determinism
    ledger_hash = compute_piece_ledger_sha256(result_data["piece_score_ledger"])
    assert len(ledger_hash) == 64

    matrix_hash = compute_replicate_matrix_sha256(boot_matrix)
    assert len(matrix_hash) == 64
    assert result_data["secondary_metrics"]["bootstrap_replicate_matrix_sha256"] == matrix_hash

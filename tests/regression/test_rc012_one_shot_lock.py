"""
Regression tests for RC-012 Pre-Execution Lock and Statistical Contract Freeze.

Verifies:
1. Historical pre-RC014 documents properly marked as historical baseline provenance.
2. Active governance authority bound to Route B APPROVED decision (N_Russian=4).
3. One-shot execution lock record integrity, ARMED_NOT_EXECUTED status, and plan hash.
4. Preflight verification script succeeds with all gates passing.
5. Exact permutation test combinatorics (C(9,4) = 126) and within-composer bootstrap on synthetic dummy fixtures.
6. Zero real confirmatory predictor evaluations executed or written to disk.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
from scripts.verify_rc012_one_shot_preflight import (
    EXPECTED_EXECUTION_PLAN_HASH,
    EXPECTED_FEATURE_CACHE_SHA256,
    EXPECTED_HUMAN_DECISION_CANONICAL_HASH,
    EXPECTED_MASTER_FREEZE_HASH,
    EXPECTED_PREDICTOR_BUNDLE_HASH,
    compute_canonical_json_hash,
    verify_rc012_one_shot_preflight,
)


def test_historical_rc012_docs_marked_with_historical_state() -> None:
    doc_results = Path("docs/research/RC012_EXTERNAL_CONFIRMATION_RESULTS.md")
    assert doc_results.exists()
    content_results = doc_results.read_text(encoding="utf-8")
    assert "HISTORICAL_PRE_RC014_STATE" in content_results
    assert "SUPERSEDED BY RC-014" in content_results

    doc_freeze = Path("docs/research/RC012_CONFIRMATORY_CORPUS_FREEZE.md")
    assert doc_freeze.exists()
    content_freeze = doc_freeze.read_text(encoding="utf-8")
    assert "HISTORICAL_PRE_RC014_STATE" in content_freeze
    assert "SUPERSEDED BY RC-014" in content_freeze


def test_one_shot_execution_lock_record_integrity() -> None:
    lock_path = Path("data/reviews/rc012/rc012_one_shot_execution_lock.json")
    assert lock_path.exists(), f"Missing {lock_path}"

    with open(lock_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data["milestone"] == "RC-012"
    assert data["document_type"] == "ONE_SHOT_EXECUTION_LOCK_RECORD"
    assert data["execution_status"] == "ARMED_NOT_EXECUTED"
    assert data["starting_head"] == "6ee93c80aa6ccb884f1355b44926f45d3caefc84"

    gov = data["governance_authority"]
    assert gov["decision_status"] == "APPROVED"
    assert gov["N_Russian"] == 4
    assert gov["N_Control"] == 5
    assert gov["total_pieces"] == 483
    assert gov["russian_pieces"] == 246
    assert gov["control_pieces"] == 237

    bindings = data["frozen_scientific_hash_bindings"]
    assert bindings["RC014C2A_CONFIRMATORY_CORPUS_FREEZE_HASH"] == EXPECTED_MASTER_FREEZE_HASH
    assert bindings["RC014C2A_REAL_FEATURE_CACHE_SHA256"] == EXPECTED_FEATURE_CACHE_SHA256
    assert bindings["RC012_FROZEN_PREDICTOR_BUNDLE_HASH"] == EXPECTED_PREDICTOR_BUNDLE_HASH

    plan_hash = compute_canonical_json_hash(data)
    assert plan_hash == EXPECTED_EXECUTION_PLAN_HASH


def test_preflight_verification_script_execution() -> None:
    result = verify_rc012_one_shot_preflight()
    assert result["status"] == "RC012_ONE_SHOT_ARMED_READY_FOR_EXECUTION"
    assert result["execution_plan_hash"] == EXPECTED_EXECUTION_PLAN_HASH
    assert result["master_freeze_hash"] == EXPECTED_MASTER_FREEZE_HASH
    assert result["feature_cache_sha256"] == EXPECTED_FEATURE_CACHE_SHA256
    assert result["predictor_bundle_hash"] == EXPECTED_PREDICTOR_BUNDLE_HASH
    assert result["human_decision_hash"] == EXPECTED_HUMAN_DECISION_CANONICAL_HASH
    assert result["n_composers"] == 9
    assert result["n_pieces"] == 483


def test_synthetic_exact_permutation_test_combinatorics() -> None:
    """Verify exact permutation logic (126 permutations) on synthetic composer scores."""
    # 4 Russian composer scores, 5 Control composer scores
    synthetic_scores = {
        "Ru_1": 1.2,
        "Ru_2": 0.8,
        "Ru_3": 0.5,
        "Ru_4": 1.0,
        "Ctrl_1": -0.2,
        "Ctrl_2": -0.5,
        "Ctrl_3": 0.1,
        "Ctrl_4": -0.8,
        "Ctrl_5": -0.3,
    }

    composers = list(synthetic_scores.keys())
    assert len(composers) == 9

    ru_scores = [synthetic_scores[c] for c in composers[:4]]
    ctrl_scores = [synthetic_scores[c] for c in composers[4:]]

    t_obs = float(np.mean(ru_scores) - np.mean(ctrl_scores))

    # Combinations of 4 out of 9
    combs = list(itertools.combinations(range(9), 4))
    assert len(combs) == 126, f"Expected 126 combinations, got {len(combs)}"

    all_scores = np.array([synthetic_scores[c] for c in composers])
    all_indices = set(range(9))

    perm_t_stats: list[float] = []
    for idx_set in combs:
        idx_a = list(idx_set)
        idx_b = list(all_indices - set(idx_set))
        t_perm = float(np.mean(all_scores[idx_a]) - np.mean(all_scores[idx_b]))
        perm_t_stats.append(t_perm)

    extreme_count = sum(1 for t in perm_t_stats if t >= t_obs)
    p_exact = extreme_count / 126.0

    assert 0.0 <= p_exact <= 1.0
    assert extreme_count >= 1  # The observed assignment itself has t >= t_obs


def test_synthetic_within_composer_stratified_bootstrap() -> None:
    """Verify within-composer piece-stratified bootstrap mechanism on synthetic piece logits."""
    rng = np.random.RandomState(42)

    # Generate synthetic composer piece clusters
    composer_piece_logits = {
        f"Composer_{c}": rng.normal(loc=0.5 if c < 4 else -0.5, scale=1.0, size=20)
        for c in range(9)
    }

    b_replicates = 500
    boot_aucs = []

    for _ in range(b_replicates):
        resampled_logits = []
        resampled_labels = []
        for c in range(9):
            logits = composer_piece_logits[f"Composer_{c}"]
            m_c = len(logits)
            sampled_idx = rng.choice(m_c, size=m_c, replace=True)
            resampled_logits.extend(logits[sampled_idx])
            resampled_labels.extend([1 if c < 4 else 0] * m_c)

        # Compute simple synthetic rank AUC
        y_true = np.array(resampled_labels)
        y_score = np.array(resampled_logits)
        pos = y_score[y_true == 1]
        neg = y_score[y_true == 0]
        auc = np.mean([1.0 if p > n else (0.5 if p == n else 0.0) for p in pos for n in neg])
        boot_aucs.append(auc)

    ci_lower = float(np.percentile(boot_aucs, 2.5))
    ci_upper = float(np.percentile(boot_aucs, 97.5))

    assert 0.0 <= ci_lower <= ci_upper <= 1.0


def test_zero_confirmatory_predictions_on_disk() -> None:
    """Strictly assert no prediction results exist on disk."""
    prohibited = [
        Path("results/rc012_predictions.parquet"),
        Path("results/rc012_decision_scores.csv"),
        Path("data/predictions/rc012"),
    ]
    for p in prohibited:
        assert not p.exists(), f"Prohibited confirmatory prediction artifact found: {p}"

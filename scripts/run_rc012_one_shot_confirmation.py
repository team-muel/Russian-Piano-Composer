"""
RC-012 One-Shot Independent External Composer Confirmation Runner.
Executes the preregistered, frozen confirmatory statistical contract exactly once.

Strict Execution Rules:
1. Anti-Rerun Guard: Terminates immediately if authoritative result artifacts exist.
2. Mandatory Preflight: All 5 cryptographic hash bindings must match perfectly.
3. Sole Feature Ordering Authority: predictor.feature_names (56 descriptors).
4. Equal Composer Weighting: S_c = mean_{i in c}(z_i) across all 9 composers.
5. Primary Statistic: T_obs = mean_{c in Russian}(S_c) - mean_{c in Control}(S_c).
6. Exact Permutation Test: C(9,4) = 126 combinatorial partitions, p_exact = count(T_A >= T_obs) / 126.
7. Secondary Metrics: AUROC, Balanced Accuracy (threshold 0.5), Brier Score.
8. Frozen Bootstrap: B = 10,000 within-composer stratified replicates, seed 42, method='linear'.
9. Strictly zero individual feature significance testing / post-hoc descriptor search.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, roc_auc_score

from scripts.verify_rc012_one_shot_preflight import (
    EXPECTED_CONTROL_COMPOSERS,
    EXPECTED_EXECUTION_PLAN_HASH,
    EXPECTED_FEATURE_CACHE_SHA256,
    EXPECTED_HUMAN_DECISION_CANONICAL_HASH,
    EXPECTED_MASTER_FREEZE_HASH,
    EXPECTED_PREDICTOR_BUNDLE_HASH,
    EXPECTED_RUSSIAN_COMPOSERS,
    compute_canonical_json_hash,
    verify_rc012_one_shot_preflight,
)

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

RESULT_PATH = Path("data/reviews/rc012/rc012_one_shot_confirmatory_result.json")
RECEIPT_PATH = Path("data/reviews/rc012/rc012_one_shot_execution_receipt.json")
BOOTSTRAP_REPLICATES_PATH = Path("data/reviews/rc012/rc012_one_shot_bootstrap_replicates.json")

BOOTSTRAP_RNG_ENGINE = "NUMPY_RANDOMSTATE_MT19937"
BOOTSTRAP_SEED = 42
BOOTSTRAP_REPLICATES_B = 10000
BOOTSTRAP_PERCENTILE_METHOD = "linear"
PRIMARY_ALPHA = 0.05


def compute_replicate_matrix_sha256(matrix: np.ndarray) -> str:
    """Compute deterministic SHA-256 of the 10,000 x 3 float64 bootstrap matrix."""
    contiguous_bytes = np.ascontiguousarray(matrix, dtype=np.float64).tobytes()
    return hashlib.sha256(contiguous_bytes).hexdigest()


def compute_piece_ledger_sha256(piece_ledger: list[dict[str, Any]]) -> str:
    """Compute canonical SHA-256 over piece-score ledger."""
    canonical_bytes = json.dumps(piece_ledger, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest()


def run_confirmatory_pipeline(
    cache_data: dict[str, Any],
    bundle_data: dict[str, Any],
    runner_commit_sha: str,
) -> tuple[dict[str, Any], dict[str, Any], np.ndarray]:
    """
    Pure statistical execution function.
    Takes feature cache and predictor bundle dicts, executes the statistical contract,
    and returns (result_dict, receipt_dict, bootstrap_matrix).
    """
    feature_names: list[str] = bundle_data["feature_names"]
    if len(feature_names) != 56:
        raise ValueError(f"Expected 56 feature names in predictor bundle, got {len(feature_names)}")

    scaler_mean = np.array(bundle_data["scaler"]["mean"], dtype=np.float64)
    scaler_scale = np.array(bundle_data["scaler"]["scale"], dtype=np.float64)
    coefficients = np.array(bundle_data["coefficients"], dtype=np.float64)
    intercept = float(bundle_data["intercept"])

    cached_pieces: list[dict[str, Any]] = cache_data["cached_pieces"]
    if len(cached_pieces) != 483:
        raise ValueError(f"Expected 483 pieces in cache, got {len(cached_pieces)}")

    # 1. Piece-Level Feature Projection, Standardization, and Scoring
    piece_ledger: list[dict[str, Any]] = []
    z_scores: list[float] = []
    probabilities: list[float] = []
    binary_predictions: list[int] = []
    true_classes: list[int] = []

    composer_to_piece_indices: dict[str, list[int]] = {c: [] for c in EXPECTED_RUSSIAN_COMPOSERS | EXPECTED_CONTROL_COMPOSERS}

    for idx, piece in enumerate(cached_pieces):
        piece_id = piece["piece_id"]
        composer = piece["composer"]
        if composer not in composer_to_piece_indices:
            raise ValueError(f"Unrecognized composer: {composer}")

        is_russian = composer in EXPECTED_RUSSIAN_COMPOSERS
        true_class = 1 if is_russian else 0
        true_classes.append(true_class)
        composer_to_piece_indices[composer].append(idx)

        features_56 = piece["features_56"]
        x_raw = np.array([features_56[name] for name in feature_names], dtype=np.float64)
        if len(x_raw) != 56 or not np.all(np.isfinite(x_raw)):
            raise ValueError(f"Non-finite or invalid feature vector for piece {piece_id}")

        x_scaled = (x_raw - scaler_mean) / scaler_scale
        z_i = float(intercept + np.dot(coefficients, x_scaled))
        p_i = float(1.0 / (1.0 + np.exp(-z_i)))
        y_hat_i = 1 if z_i >= 0.0 else 0

        z_scores.append(z_i)
        probabilities.append(p_i)
        binary_predictions.append(y_hat_i)

        piece_ledger.append({
            "piece_id": piece_id,
            "composer": composer,
            "true_class": "Russian" if is_russian else "Control",
            "true_label": true_class,
            "z_i": z_i,
            "p_i": p_i,
            "y_hat_i": y_hat_i,
        })

    piece_ledger_hash = compute_piece_ledger_sha256(piece_ledger)

    # 2. Composer-Level Aggregation S_c
    composer_scores: dict[str, float] = {}
    for composer, piece_idxs in composer_to_piece_indices.items():
        if len(piece_idxs) < 10:
            raise ValueError(f"Composer {composer} has Mc={len(piece_idxs)} < 10")
        c_z = [z_scores[i] for i in piece_idxs]
        composer_scores[composer] = float(np.mean(c_z))

    # 3. Primary Statistic T_obs
    russian_c_scores = [composer_scores[c] for c in sorted(EXPECTED_RUSSIAN_COMPOSERS)]
    control_c_scores = [composer_scores[c] for c in sorted(EXPECTED_CONTROL_COMPOSERS)]

    russian_mean_score = float(np.mean(russian_c_scores))
    control_mean_score = float(np.mean(control_c_scores))
    t_obs = float(russian_mean_score - control_mean_score)

    # 4. Exact Permutation Test C(9,4) = 126
    all_9_composers = sorted(list(EXPECTED_RUSSIAN_COMPOSERS | EXPECTED_CONTROL_COMPOSERS))
    all_composer_scores_arr = np.array([composer_scores[c] for c in all_9_composers], dtype=np.float64)
    all_idx_set = set(range(9))

    comb_4_of_9 = list(itertools.combinations(range(9), 4))
    if len(comb_4_of_9) != 126:
        raise ValueError(f"Combinatorics error: expected 126 combinations, got {len(comb_4_of_9)}")

    permutation_records: list[dict[str, Any]] = []
    perm_t_stats: list[float] = []

    observed_russian_set = set(sorted(EXPECTED_RUSSIAN_COMPOSERS))

    for perm_idx, idx_subset in enumerate(comb_4_of_9, start=1):
        idx_class1 = list(idx_subset)
        idx_class0 = list(all_idx_set - set(idx_subset))

        c1_names = [all_9_composers[i] for i in idx_class1]
        c0_names = [all_9_composers[i] for i in idx_class0]

        is_obs = set(c1_names) == observed_russian_set

        t_perm = float(np.mean(all_composer_scores_arr[idx_class1]) - np.mean(all_composer_scores_arr[idx_class0]))
        perm_t_stats.append(t_perm)

        permutation_records.append({
            "assignment_index": perm_idx,
            "class_1_composers": sorted(c1_names),
            "class_0_composers": sorted(c0_names),
            "T_A": t_perm,
            "is_observed_assignment": is_obs,
        })

    # Exact p-value calculations
    extreme_count = sum(1 for t in perm_t_stats if t >= t_obs)
    strictly_greater_count = sum(1 for t in perm_t_stats if t > t_obs)
    tie_count = sum(1 for t in perm_t_stats if t == t_obs)
    p_exact = float(extreme_count / 126.0)

    sorted_t_desc = sorted(perm_t_stats, reverse=True)
    observed_rank_min = sorted_t_desc.index(t_obs) + 1
    observed_rank_max = observed_rank_min + tie_count - 1

    # Primary inferential status
    if p_exact <= PRIMARY_ALPHA and t_obs > 0.0:
        primary_inferential_status = "PRIMARY_TEST_REJECTS_NULL_IN_PREREGISTERED_DIRECTION"
    else:
        primary_inferential_status = "PRIMARY_TEST_DOES_NOT_REJECT_NULL"

    # 5. Secondary Classification Metrics
    y_true_arr = np.array(true_classes, dtype=np.int64)
    z_scores_arr = np.array(z_scores, dtype=np.float64)
    p_arr = np.array(probabilities, dtype=np.float64)
    y_hat_arr = np.array(binary_predictions, dtype=np.int64)

    secondary_auroc = float(roc_auc_score(y_true_arr, z_scores_arr))
    secondary_balanced_accuracy = float(balanced_accuracy_score(y_true_arr, y_hat_arr))
    secondary_brier_score = float(brier_score_loss(y_true_arr, p_arr))

    # 6. Frozen Within-Composer Stratified Bootstrap (B = 10,000)
    rng = np.random.RandomState(BOOTSTRAP_SEED)
    bootstrap_matrix = np.zeros((BOOTSTRAP_REPLICATES_B, 3), dtype=np.float64)

    composer_piece_arrays = {
        c: np.array(indices, dtype=np.int64)
        for c, indices in composer_to_piece_indices.items()
    }

    for b in range(BOOTSTRAP_REPLICATES_B):
        resampled_all_indices: list[int] = []
        for c in all_9_composers:
            c_indices = composer_piece_arrays[c]
            m_c = len(c_indices)
            sampled = rng.choice(c_indices, size=m_c, replace=True)
            resampled_all_indices.extend(sampled.tolist())

        res_idx_arr = np.array(resampled_all_indices, dtype=np.int64)
        b_y_true = y_true_arr[res_idx_arr]
        b_z = z_scores_arr[res_idx_arr]
        b_p = p_arr[res_idx_arr]
        b_y_hat = y_hat_arr[res_idx_arr]

        b_auroc = float(roc_auc_score(b_y_true, b_z))
        b_bal_acc = float(balanced_accuracy_score(b_y_true, b_y_hat))
        b_brier = float(brier_score_loss(b_y_true, b_p))

        bootstrap_matrix[b, 0] = b_auroc
        bootstrap_matrix[b, 1] = b_bal_acc
        bootstrap_matrix[b, 2] = b_brier

    bootstrap_replicate_matrix_sha256 = compute_replicate_matrix_sha256(bootstrap_matrix)

    # 95% Percentile Confidence Intervals
    auroc_ci = [float(v) for v in np.percentile(bootstrap_matrix[:, 0], [2.5, 97.5], method=BOOTSTRAP_PERCENTILE_METHOD)]
    bal_acc_ci = [float(v) for v in np.percentile(bootstrap_matrix[:, 1], [2.5, 97.5], method=BOOTSTRAP_PERCENTILE_METHOD)]
    brier_ci = [float(v) for v in np.percentile(bootstrap_matrix[:, 2], [2.5, 97.5], method=BOOTSTRAP_PERCENTILE_METHOD)]

    # 7. Construct Authoritative Confirmatory Result Document
    result_payload: dict[str, Any] = {
        "milestone": "RC-012",
        "document_type": "CONFIRMATORY_ONE_SHOT_EXECUTION_RESULT",
        "execution_status": "COMPLETED_AUTHORITATIVE",
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runner_commit": runner_commit_sha,
        "runtime_environment": {
            "numpy_version": np.__version__,
            "bootstrap_rng_engine": BOOTSTRAP_RNG_ENGINE,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_replicates_B": BOOTSTRAP_REPLICATES_B,
            "bootstrap_percentile_method": BOOTSTRAP_PERCENTILE_METHOD,
        },
        "frozen_input_hash_bindings": {
            "RC014C2A_CONFIRMATORY_CORPUS_FREEZE_HASH": EXPECTED_MASTER_FREEZE_HASH,
            "RC014C2A_REAL_FEATURE_CACHE_SHA256": EXPECTED_FEATURE_CACHE_SHA256,
            "RC012_FROZEN_PREDICTOR_BUNDLE_HASH": EXPECTED_PREDICTOR_BUNDLE_HASH,
            "HUMAN_ACCESS_DECISION_CANONICAL_HASH": EXPECTED_HUMAN_DECISION_CANONICAL_HASH,
            "RC012_ONE_SHOT_EXECUTION_PLAN_HASH": EXPECTED_EXECUTION_PLAN_HASH,
        },
        "repertoire_summary": {
            "total_pieces": 483,
            "total_composers": 9,
            "russian_composers_count": 4,
            "control_composers_count": 5,
            "russian_pieces_count": 246,
            "control_pieces_count": 237,
            "piece_ledger_sha256": piece_ledger_hash,
        },
        "piece_score_ledger": piece_ledger,
        "composer_level_scores": composer_scores,
        "primary_hypothesis_result": {
            "statistic_name": "T_obs",
            "T_obs": t_obs,
            "russian_mean_score": russian_mean_score,
            "control_mean_score": control_mean_score,
            "permutation_count": 126,
            "extreme_count": extreme_count,
            "strictly_greater_count": strictly_greater_count,
            "tie_count": tie_count,
            "observed_rank_min": observed_rank_min,
            "observed_rank_max": observed_rank_max,
            "p_exact": p_exact,
            "alpha": PRIMARY_ALPHA,
            "primary_inferential_status": primary_inferential_status,
            "all_126_permutation_assignments": permutation_records,
        },
        "secondary_metrics": {
            "auroc": {
                "point_estimate": secondary_auroc,
                "ci_95_percentile": auroc_ci,
            },
            "balanced_accuracy": {
                "point_estimate": secondary_balanced_accuracy,
                "ci_95_percentile": bal_acc_ci,
                "decision_threshold": 0.5,
            },
            "brier_score": {
                "point_estimate": secondary_brier_score,
                "ci_95_percentile": brier_ci,
            },
            "bootstrap_replicate_matrix_sha256": bootstrap_replicate_matrix_sha256,
        },
        "feature_battery_status": {
            "56_feature_significance_battery": "EXCLUDED_FROM_ONE_SHOT_CONFIRMATION",
            "rationale": "Preregistered strict FWER protection and single-endpoint confirmation.",
        },
    }

    result_hash = compute_canonical_json_hash(result_payload)
    result_payload["confirmatory_result_hash"] = result_hash

    # 8. Construct Immutable Execution Receipt
    receipt_payload: dict[str, Any] = {
        "milestone": "RC-012",
        "document_type": "ONE_SHOT_EXECUTION_RECEIPT",
        "execution_status": "EXECUTED",
        "execution_timestamp": result_payload["timestamp_iso"],
        "starting_runner_commit": runner_commit_sha,
        "execution_plan_hash": EXPECTED_EXECUTION_PLAN_HASH,
        "corpus_freeze_hash": EXPECTED_MASTER_FREEZE_HASH,
        "feature_cache_hash": EXPECTED_FEATURE_CACHE_SHA256,
        "predictor_bundle_hash": EXPECTED_PREDICTOR_BUNDLE_HASH,
        "human_decision_hash": EXPECTED_HUMAN_DECISION_CANONICAL_HASH,
        "result_hash": result_hash,
        "piece_score_ledger_hash": piece_ledger_hash,
        "bootstrap_replicate_matrix_sha256": bootstrap_replicate_matrix_sha256,
        "primary_inferential_status": primary_inferential_status,
        "T_obs": t_obs,
        "p_exact": p_exact,
        "secondary_auroc": secondary_auroc,
        "secondary_balanced_accuracy": secondary_balanced_accuracy,
        "secondary_brier_score": secondary_brier_score,
    }

    return result_payload, receipt_payload, bootstrap_matrix


def execute_one_shot_confirmation() -> dict[str, Any]:
    print("==========================================================================")
    print(" RC-012 ONE-SHOT CONFIRMATORY EXECUTION INITIATING")
    print("==========================================================================")

    # Phase 3. One-Shot Existence Guard
    if RESULT_PATH.exists() or RECEIPT_PATH.exists():
        raise RuntimeError("RC012_ALREADY_EXECUTED: Authoritative execution artifact already exists. Refusing rerun.")

    # Phase 2. Mandatory Preflight
    preflight_result = verify_rc012_one_shot_preflight()
    if preflight_result.get("status") != "RC012_ONE_SHOT_ARMED_READY_FOR_EXECUTION":
        raise RuntimeError("Preflight check failed to confirm ARMED status")

    # Get current runner commit SHA
    import subprocess
    runner_commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()

    # Phase 4. Load Frozen Inputs
    cache_path = Path("data/manifests/rc014c2a_complete_role_blind_feature_cache.json")
    with open(cache_path, encoding="utf-8") as f:
        cache_data = json.load(f)

    bundle_path = Path("models/rc012_predictor/frozen_predictor_bundle.json")
    if not bundle_path.exists():
        bundle_path = Path("data/manifests/rc012_frozen_predictor_bundle.json")
    with open(bundle_path, encoding="utf-8") as f:
        bundle_data = json.load(f)

    # Phases 5-17. Statistical Execution
    result_data, receipt_data, bootstrap_matrix = run_confirmatory_pipeline(
        cache_data=cache_data,
        bundle_data=bundle_data,
        runner_commit_sha=runner_commit_sha,
    )

    # Persist bootstrap replicates
    bootstrap_records = {
        "milestone": "RC-012",
        "description": "10,000 within-composer stratified bootstrap replicate metrics (AUROC, Balanced Accuracy, Brier Score)",
        "bootstrap_replicate_matrix_sha256": result_data["secondary_metrics"]["bootstrap_replicate_matrix_sha256"],
        "replicates_B": BOOTSTRAP_REPLICATES_B,
        "metrics": ["auroc", "balanced_accuracy", "brier_score"],
        "replicate_values": bootstrap_matrix.tolist(),
    }
    with open(BOOTSTRAP_REPLICATES_PATH, "w", encoding="utf-8") as f:
        json.dump(bootstrap_records, f, indent=2)

    # Phase 18. Persist Result Artifact
    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2)

    # Phase 19. Persist Execution Receipt
    with open(RECEIPT_PATH, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, indent=2)

    print("\n==========================================================================")
    print(" RC-012 ONE-SHOT CONFIRMATORY EXECUTION COMPLETED")
    print(f" PRIMARY STATISTIC T_obs = {result_data['primary_hypothesis_result']['T_obs']:.6f}")
    print(f" EXACT P-VALUE p_exact   = {result_data['primary_hypothesis_result']['p_exact']:.6f} ({result_data['primary_hypothesis_result']['extreme_count']}/126)")
    print(f" PRIMARY INFERENTIAL STATUS: {result_data['primary_hypothesis_result']['primary_inferential_status']}")
    print(f" SECONDARY AUROC         = {result_data['secondary_metrics']['auroc']['point_estimate']:.4f} {result_data['secondary_metrics']['auroc']['ci_95_percentile']}")
    print(f" SECONDARY BAL. ACCURACY = {result_data['secondary_metrics']['balanced_accuracy']['point_estimate']:.4f} {result_data['secondary_metrics']['balanced_accuracy']['ci_95_percentile']}")
    print(f" SECONDARY BRIER SCORE   = {result_data['secondary_metrics']['brier_score']['point_estimate']:.4f} {result_data['secondary_metrics']['brier_score']['ci_95_percentile']}")
    print("==========================================================================")

    return result_data


def main() -> None:
    execute_one_shot_confirmation()


if __name__ == "__main__":
    main()

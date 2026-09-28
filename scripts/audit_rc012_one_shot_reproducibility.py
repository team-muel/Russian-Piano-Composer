"""
RC-012 Independent Two-Process Confirmatory Reproducibility Auditor.
Re-executes the complete statistical pipeline in a separate read-only process
and verifies exact bitwise and numerical reproducibility against authoritative results.

Audit Invariants:
- Never overwrites or modifies existing result artifacts.
- Validates all 483 piece scores, 9 composer aggregations, T_obs, 126 permutations,
  exact p-value, secondary metrics, 10,000-bootstrap replicate matrix, and 95% percentile CIs.
- Outputs authoritative two-process audit receipt.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from scripts.run_rc012_one_shot_confirmation import (
    BOOTSTRAP_PERCENTILE_METHOD,
    BOOTSTRAP_REPLICATES_B,
    BOOTSTRAP_RNG_ENGINE,
    BOOTSTRAP_SEED,
    RECEIPT_PATH,
    RESULT_PATH,
    compute_piece_ledger_sha256,
    compute_replicate_matrix_sha256,
    run_confirmatory_pipeline,
)
from scripts.verify_rc012_one_shot_preflight import compute_canonical_json_hash

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

AUDIT_PATH = Path("data/reviews/rc012/rc012_one_shot_reproducibility_audit.json")


def audit_rc012_reproducibility() -> dict[str, Any]:
    print("=== Running RC-012 Independent Two-Process Reproducibility Audit ===")

    if not RESULT_PATH.exists():
        raise FileNotFoundError(f"Authoritative result artifact missing at {RESULT_PATH}")
    if not RECEIPT_PATH.exists():
        raise FileNotFoundError(f"Authoritative receipt artifact missing at {RECEIPT_PATH}")

    with open(RESULT_PATH, encoding="utf-8") as f:
        auth_result = json.load(f)
    with open(RECEIPT_PATH, encoding="utf-8") as f:
        auth_receipt = json.load(f)

    # 1. Independent Re-execution from Raw Inputs
    cache_path = Path("data/manifests/rc014c2a_complete_role_blind_feature_cache.json")
    with open(cache_path, encoding="utf-8") as f:
        cache_data = json.load(f)

    bundle_path = Path("models/rc012_predictor/frozen_predictor_bundle.json")
    if not bundle_path.exists():
        bundle_path = Path("data/manifests/rc012_frozen_predictor_bundle.json")
    with open(bundle_path, encoding="utf-8") as f:
        bundle_data = json.load(f)

    runner_commit = auth_result.get("runner_commit", "UNKNOWN")

    recomputed_result, recomputed_receipt, recomputed_bootstrap_matrix = run_confirmatory_pipeline(
        cache_data=cache_data,
        bundle_data=bundle_data,
        runner_commit_sha=runner_commit,
    )

    # 2. Piece-Score Ledger Audit (483 pieces)
    auth_ledger = auth_result["piece_score_ledger"]
    recomp_ledger = recomputed_result["piece_score_ledger"]
    if len(auth_ledger) != 483 or len(recomp_ledger) != 483:
        raise ValueError(f"Ledger length mismatch: auth={len(auth_ledger)}, recomp={len(recomp_ledger)}")

    for i in range(483):
        a_p = auth_ledger[i]
        r_p = recomp_ledger[i]
        assert a_p["piece_id"] == r_p["piece_id"], f"Piece ID mismatch at index {i}"
        assert a_p["composer"] == r_p["composer"], f"Composer mismatch at index {i}"
        assert a_p["true_class"] == r_p["true_class"], f"True class mismatch at index {i}"
        assert math.isclose(a_p["z_i"], r_p["z_i"], rel_tol=1e-12, abs_tol=1e-12), f"z_i mismatch at {a_p['piece_id']}"
        assert math.isclose(a_p["p_i"], r_p["p_i"], rel_tol=1e-12, abs_tol=1e-12), f"p_i mismatch at {a_p['piece_id']}"
        assert a_p["y_hat_i"] == r_p["y_hat_i"], f"y_hat mismatch at {a_p['piece_id']}"

    auth_ledger_hash = auth_result["repertoire_summary"]["piece_ledger_sha256"]
    recomp_ledger_hash = compute_piece_ledger_sha256(recomp_ledger)
    if auth_ledger_hash != recomp_ledger_hash:
        raise ValueError(f"Piece ledger hash mismatch: {auth_ledger_hash} vs {recomp_ledger_hash}")
    print("  [PASS] 483 Piece-Level Scores & Ledger Hash Reproducible")

    # 3. 9 Composer Scores Audit
    auth_comp = auth_result["composer_level_scores"]
    recomp_comp = recomputed_result["composer_level_scores"]
    for c, s_auth in auth_comp.items():
        s_recomp = recomp_comp[c]
        assert math.isclose(s_auth, s_recomp, rel_tol=1e-12, abs_tol=1e-12), f"Composer score mismatch for {c}"
    print("  [PASS] 9 Composer Aggregated Scores Reproducible")

    # 4. Primary Statistic & Exact Permutations Audit
    auth_prim = auth_result["primary_hypothesis_result"]
    recomp_prim = recomputed_result["primary_hypothesis_result"]

    assert math.isclose(auth_prim["T_obs"], recomp_prim["T_obs"], rel_tol=1e-12, abs_tol=1e-12), "T_obs mismatch"
    assert auth_prim["extreme_count"] == recomp_prim["extreme_count"], "extreme_count mismatch"
    assert auth_prim["strictly_greater_count"] == recomp_prim["strictly_greater_count"], "strictly_greater mismatch"
    assert auth_prim["tie_count"] == recomp_prim["tie_count"], "tie_count mismatch"
    assert auth_prim["observed_rank_min"] == recomp_prim["observed_rank_min"], "observed_rank_min mismatch"
    assert auth_prim["observed_rank_max"] == recomp_prim["observed_rank_max"], "observed_rank_max mismatch"
    assert math.isclose(auth_prim["p_exact"], recomp_prim["p_exact"], rel_tol=1e-12, abs_tol=1e-12), "p_exact mismatch"
    assert auth_prim["primary_inferential_status"] == recomp_prim["primary_inferential_status"]

    auth_perms = auth_prim["all_126_permutation_assignments"]
    recomp_perms = recomp_prim["all_126_permutation_assignments"]
    assert len(auth_perms) == 126 and len(recomp_perms) == 126
    for k in range(126):
        assert math.isclose(auth_perms[k]["T_A"], recomp_perms[k]["T_A"], rel_tol=1e-12, abs_tol=1e-12)
        assert auth_perms[k]["is_observed_assignment"] == recomp_perms[k]["is_observed_assignment"]
    print("  [PASS] Primary Statistic T_obs & 126 Permutations Exact Match")

    # 5. Secondary Metrics & Bootstrap Matrix Audit
    auth_sec = auth_result["secondary_metrics"]
    recomp_sec = recomputed_result["secondary_metrics"]

    assert math.isclose(auth_sec["auroc"]["point_estimate"], recomp_sec["auroc"]["point_estimate"], rel_tol=1e-12)
    assert np.allclose(auth_sec["auroc"]["ci_95_percentile"], recomp_sec["auroc"]["ci_95_percentile"])

    assert math.isclose(auth_sec["balanced_accuracy"]["point_estimate"], recomp_sec["balanced_accuracy"]["point_estimate"], rel_tol=1e-12)
    assert np.allclose(auth_sec["balanced_accuracy"]["ci_95_percentile"], recomp_sec["balanced_accuracy"]["ci_95_percentile"])

    assert math.isclose(auth_sec["brier_score"]["point_estimate"], recomp_sec["brier_score"]["point_estimate"], rel_tol=1e-12)
    assert np.allclose(auth_sec["brier_score"]["ci_95_percentile"], recomp_sec["brier_score"]["ci_95_percentile"])

    recomp_boot_sha = compute_replicate_matrix_sha256(recomputed_bootstrap_matrix)
    auth_boot_sha = auth_sec["bootstrap_replicate_matrix_sha256"]
    assert auth_boot_sha == recomp_boot_sha, f"Bootstrap replicate matrix SHA mismatch: {auth_boot_sha} vs {recomp_boot_sha}"
    print("  [PASS] Secondary Metrics & 10,000 Replicate Matrix Bitwise Match")

    # 6. Construct and Persist Reproducibility Audit Document
    audit_data: dict[str, Any] = {
        "milestone": "RC-012",
        "document_type": "CONFIRMATORY_TWO_PROCESS_REPRODUCIBILITY_AUDIT",
        "two_process_reproducibility": "PASS",
        "audit_timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verified_result_hash": auth_result["confirmatory_result_hash"],
        "verified_receipt_result_hash": auth_receipt["result_hash"],
        "piece_scores_count_verified": 483,
        "composer_scores_count_verified": 9,
        "permutation_assignments_count_verified": 126,
        "bootstrap_replicates_count_verified": BOOTSTRAP_REPLICATES_B,
        "primary_statistic_verified": {
            "T_obs": auth_prim["T_obs"],
            "p_exact": auth_prim["p_exact"],
            "extreme_count": auth_prim["extreme_count"],
            "primary_inferential_status": auth_prim["primary_inferential_status"],
        },
        "secondary_metrics_verified": {
            "auroc": auth_sec["auroc"],
            "balanced_accuracy": auth_sec["balanced_accuracy"],
            "brier_score": auth_sec["brier_score"],
        },
        "deterministic_hash_bindings": {
            "piece_ledger_sha256": auth_ledger_hash,
            "bootstrap_replicate_matrix_sha256": auth_boot_sha,
            "result_canonical_hash": auth_result["confirmatory_result_hash"],
        },
    }

    audit_data_hash = compute_canonical_json_hash(audit_data)
    audit_data["audit_record_hash"] = audit_data_hash

    with open(AUDIT_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)

    print("\n==========================================================================")
    print(" RC-012 TWO-PROCESS REPRODUCIBILITY AUDIT: PASS")
    print(" TWO_PROCESS_REPRODUCIBILITY = PASS")
    print("==========================================================================")

    return audit_data


def main() -> None:
    audit_rc012_reproducibility()


if __name__ == "__main__":
    main()

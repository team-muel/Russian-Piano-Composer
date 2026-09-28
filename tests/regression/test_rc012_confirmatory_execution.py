"""
Regression tests for RC-012 One-Shot Independent External Composer Confirmation.
Validates the authoritative post-execution artifacts, primary inferential decision,
secondary metrics, hash bindings, and independent two-process reproducibility audit.
"""

from __future__ import annotations

import json
import math

import pytest
from scripts.audit_rc012_one_shot_reproducibility import AUDIT_PATH
from scripts.run_rc012_one_shot_confirmation import (
    RECEIPT_PATH,
    RESULT_PATH,
    execute_one_shot_confirmation,
)

FROZEN_CONFIRMATORY_RESULT_HASH = "a933ac2b21fe50cff9c0a43e8216ee37593acded32e22ecb0e9502b231cffded"
FROZEN_PIECE_LEDGER_HASH = "66513dc4901b48ee865ba826cb4dad824f448b242b94834fd25202d39c5aa634"
FROZEN_BOOTSTRAP_MATRIX_HASH = "d606705dd1621a4b0fef85c1dbec2f2f1347891c8576a2162e64ac9306b5b739"


def test_authoritative_result_artifact_integrity() -> None:
    assert RESULT_PATH.exists(), f"Missing {RESULT_PATH}"

    with open(RESULT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    assert data["milestone"] == "RC-012"
    assert data["document_type"] == "CONFIRMATORY_ONE_SHOT_EXECUTION_RESULT"
    assert data["execution_status"] == "COMPLETED_AUTHORITATIVE"
    assert data["confirmatory_result_hash"] == FROZEN_CONFIRMATORY_RESULT_HASH

    rep = data["repertoire_summary"]
    assert rep["total_pieces"] == 483
    assert rep["total_composers"] == 9
    assert rep["russian_composers_count"] == 4
    assert rep["control_composers_count"] == 5
    assert rep["russian_pieces_count"] == 246
    assert rep["control_pieces_count"] == 237
    assert rep["piece_ledger_sha256"] == FROZEN_PIECE_LEDGER_HASH

    assert len(data["piece_score_ledger"]) == 483
    assert len(data["composer_level_scores"]) == 9


def test_primary_inferential_decision_and_permutations() -> None:
    with open(RESULT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    prim = data["primary_hypothesis_result"]
    assert math.isclose(prim["T_obs"], -0.7343332388718129, rel_tol=1e-9)
    assert prim["permutation_count"] == 126
    assert prim["extreme_count"] == 110
    assert prim["strictly_greater_count"] == 109
    assert prim["tie_count"] == 1
    assert prim["observed_rank_min"] == 110
    assert prim["observed_rank_max"] == 110
    assert math.isclose(prim["p_exact"], 110.0 / 126.0, rel_tol=1e-9)
    assert prim["primary_inferential_status"] == "PRIMARY_TEST_DOES_NOT_REJECT_NULL"


def test_secondary_metrics_and_bootstrap_intervals() -> None:
    with open(RESULT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    sec = data["secondary_metrics"]
    assert math.isclose(sec["auroc"]["point_estimate"], 0.5113203663682206, rel_tol=1e-6)
    assert math.isclose(sec["balanced_accuracy"]["point_estimate"], 0.5160543377585675, rel_tol=1e-6)
    assert math.isclose(sec["brier_score"]["point_estimate"], 0.2659867577132047, rel_tol=1e-6)
    assert sec["bootstrap_replicate_matrix_sha256"] == FROZEN_BOOTSTRAP_MATRIX_HASH


def test_execution_receipt_integrity() -> None:
    assert RECEIPT_PATH.exists(), f"Missing {RECEIPT_PATH}"

    with open(RECEIPT_PATH, encoding="utf-8") as f:
        receipt = json.load(f)

    assert receipt["milestone"] == "RC-012"
    assert receipt["document_type"] == "ONE_SHOT_EXECUTION_RECEIPT"
    assert receipt["execution_status"] == "EXECUTED"
    assert receipt["result_hash"] == FROZEN_CONFIRMATORY_RESULT_HASH
    assert receipt["piece_score_ledger_hash"] == FROZEN_PIECE_LEDGER_HASH
    assert receipt["bootstrap_replicate_matrix_sha256"] == FROZEN_BOOTSTRAP_MATRIX_HASH
    assert receipt["primary_inferential_status"] == "PRIMARY_TEST_DOES_NOT_REJECT_NULL"


def test_two_process_reproducibility_audit_pass() -> None:
    assert AUDIT_PATH.exists(), f"Missing {AUDIT_PATH}"

    with open(AUDIT_PATH, encoding="utf-8") as f:
        audit = json.load(f)

    assert audit["milestone"] == "RC-012"
    assert audit["document_type"] == "CONFIRMATORY_TWO_PROCESS_REPRODUCIBILITY_AUDIT"
    assert audit["two_process_reproducibility"] == "PASS"
    assert audit["verified_result_hash"] == FROZEN_CONFIRMATORY_RESULT_HASH


def test_anti_rerun_execution_guard() -> None:
    """Invoking runner when result exists must fail closed with RC012_ALREADY_EXECUTED."""
    with pytest.raises(RuntimeError, match="RC012_ALREADY_EXECUTED"):
        execute_one_shot_confirmation()

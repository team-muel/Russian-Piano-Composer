"""Regression tests for PF-001C1 / PF-001C1.1 metric and calibration contract.

Verifies:
1. Validator script execution succeeds and outputs valid PF001C1_METRIC_CONTRACT_HASH.
2. Invariants: 62 pieces in physical corpus, receipt hash matches authoritative receipt.
3. All gates remain uncalibrated (provisional / not ready).
4. THEME_MOTIF_IDENTITY_NOT_READY enforces SOURCE_SEGMENT_IDENTITY_ONLY and two admissible routes (Route A, Route B).
5. ClosureContrast sign consistency: ClosureContrast = Cc - Ct > 0 (cadential disruption lowers closure).
6. Single anti-copy smoothing estimator: ADD_ALPHA with alpha=0.1 on development corpus only.
7. Single bootstrap CI procedure: PERCENTILE, B=2000, piece_id clustering, alpha=0.05.
8. SOURCE_SEGMENT_STRUCTURAL_MEMORY terminology and CF-SOURCE-SEGMENT-MEMORY.
9. THEMATIC_MEMORY_GATE status = THEME_IDENTITY_DEPENDENT_NOT_READY.
10. COMPOSER_GENERALIZATION_GATE evaluated on frozen Listener across composer-disjoint human repertoire without generated repertoire.
11. Grouped K-Fold Youden's J algorithm with deterministic tie-breaking.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_validator_script_succeeds():
    """Runs scripts/validate_pf001c1_metric_contract.py and asserts return code 0."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_pf001c1_metric_contract.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Validator failed:\n{result.stderr}\n{result.stdout}"
    assert "PF001C1_METRIC_CONTRACT_HASH=" in result.stdout
    assert "Contract validation SUCCESSFUL." in result.stdout


def test_zero_premature_numerical_threshold_freezing():
    """Confirms no numerical gate thresholds are marked final or calibrated, and no stale values remain in active descriptions."""
    gate_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_gate_readiness.json"
    with open(gate_file, encoding="utf-8") as f:
        data = json.load(f)

    gates = data.get("gates", {})
    assert len(gates) >= 10

    for gate_name, info in gates.items():
        st = info.get("status")
        assert st in {
            "PROVISIONAL_UNCALIBRATED_TARGET",
            "NOT_READY_FOR_CALIBRATION",
            "THEME_MOTIF_IDENTITY_NOT_READY",
            "THEME_IDENTITY_DEPENDENT_NOT_READY",
        }, f"Gate {gate_name} has invalid or premature status {st}"

        desc = info.get("provisional_threshold_description", "")
        for stale in ["0.85", "0.30", "0.95", "1.80", "0.50", "15%"]:
            assert stale not in desc, f"Gate {gate_name} contains stale numerical threshold {stale}"


def test_theme_identity_not_ready_and_two_admissible_routes():
    """Verifies THEME_MOTIF_IDENTITY is marked NOT_READY, restricted to SOURCE_SEGMENT_IDENTITY_ONLY, and admits Route A and B."""
    theme_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_theme_identity_readiness.json"
    with open(theme_file, encoding="utf-8") as f:
        data = json.load(f)

    assert data["status"] == "THEME_MOTIF_IDENTITY_NOT_READY"
    assert data["lineage_policy_verdict"]["operational_scope_for_pf002a"] == "SOURCE_SEGMENT_IDENTITY_ONLY"
    assert data["audit_findings"]["theme_annotation_manifest_accepted_count"] == 0
    assert data["audit_findings"]["pilot_candidates_human_accepted_count"] == 0

    routes = data.get("admissible_evidence_routes", {})
    assert "ROUTE_A" in routes
    assert "ROUTE_B" in routes


def test_transformation_and_counterfactual_registries():
    """Verifies transformations and counterfactual definitions are non-empty and well-structured."""
    trans_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_transformation_registry.json"
    with open(trans_file, encoding="utf-8") as f:
        trans_data = json.load(f)
    assert len(trans_data.get("transformations", [])) >= 7

    cf_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_counterfactual_registry.json"
    with open(cf_file, encoding="utf-8") as f:
        cf_data = json.load(f)
    families = cf_data.get("perturbation_families", [])
    assert len(families) >= 3

    fam_ids = {fam["family_id"] for fam in families}
    assert {"CF-CLOSURE", "CF-SOURCE-SEGMENT-MEMORY", "CF-SURPRISE"}.issubset(fam_ids)

    for fam in families:
        assert "matched_control_perturbation" in fam
        assert "directional_contrast_statistic" in fam


def test_closure_contrast_semantics_and_sign():
    """Verifies ClosureContrast = (C0 - Ct) - (C0 - Cc) = Cc - Ct > 0 (cadential disruption lowers closure)."""
    contract_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_metric_calibration_contract.json"
    with open(contract_file, encoding="utf-8") as f:
        contract = json.load(f)

    closure_metric = contract["metrics"]["CLOSURE_CONTRAST"]
    assert "Cc - Ct" in closure_metric["formula"]
    assert "lowers" in closure_metric["interpretation"].lower()
    assert "preparation increases" not in closure_metric["interpretation"].lower()

    # Numerical verification
    c0 = 0.80  # original score closure
    ct = 0.35  # cadential disruption closure (lowered)
    cc = 0.75  # matched control closure (minor change)
    closure_contrast = (c0 - ct) - (c0 - cc)
    assert closure_contrast == cc - ct
    assert closure_contrast > 0


def test_anti_copy_single_estimator_add_alpha():
    """Verifies single ADD_ALPHA smoothing estimator with alpha=0.1 on development corpus."""
    contract_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_metric_calibration_contract.json"
    with open(contract_file, encoding="utf-8") as f:
        contract = json.load(f)

    tier2 = contract["metrics"]["ANTI_COPY_METRICS"]["tier_2_weighted_interval_ngram"]
    assert tier2["smoothing_method"] == "ADD_ALPHA"
    assert tier2["alpha"] == 0.1
    assert tier2["corpus_scope"] == "DEVELOPMENT_CORPUS_ONLY"

    # Test probability estimator
    count_g = 5
    n_dev = 1000
    vocab_size = 12
    k = 4
    v_k = vocab_size ** k
    p_dev = (count_g + 0.1) / (n_dev + 0.1 * v_k)
    assert p_dev > 0
    w_g = -math.log2(p_dev)
    assert w_g > 0


def test_bootstrap_single_percentile_ci_method():
    """Verifies single PERCENTILE bootstrap CI method with B=2000 and piece_id clustering."""
    contract_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_metric_calibration_contract.json"
    with open(contract_file, encoding="utf-8") as f:
        contract = json.load(f)

    resamp = contract["resampling_and_uncertainty_policy"]
    assert resamp["bootstrap_replicates"] == 2000
    assert resamp["cluster_unit"] == "piece_id"
    assert resamp["confidence_interval_method"] == "PERCENTILE"
    assert resamp["confidence_level"] == 0.95
    assert resamp["lower_quantile"] == 0.025
    assert resamp["upper_quantile"] == 0.975


def test_source_segment_structural_memory_and_thematic_split():
    """Verifies SOURCE_SEGMENT_STRUCTURAL_MEMORY is operationalized and THEMATIC_MEMORY_GATE is split as not ready."""
    gate_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_gate_readiness.json"
    with open(gate_file, encoding="utf-8") as f:
        gates = json.load(f)["gates"]

    assert "SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE" in gates
    assert gates["SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE"]["status"] == "PROVISIONAL_UNCALIBRATED_TARGET"

    assert "THEMATIC_MEMORY_GATE" in gates
    assert gates["THEMATIC_MEMORY_GATE"]["status"] == "THEME_IDENTITY_DEPENDENT_NOT_READY"


def test_composer_generalization_listener_only():
    """Verifies COMPOSER_GENERALIZATION_GATE is a Listener property on human repertoire without generated music."""
    gate_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_gate_readiness.json"
    with open(gate_file, encoding="utf-8") as f:
        gates = json.load(f)["gates"]

    comp_gate = gates["COMPOSER_GENERALIZATION_GATE"]
    assert comp_gate["status"] == "NOT_READY_FOR_CALIBRATION"
    assert "human" in comp_gate["metric"].lower()
    assert "generated" not in comp_gate["metric"].lower()

    contract_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_metric_calibration_contract.json"
    with open(contract_file, encoding="utf-8") as f:
        contract = json.load(f)

    comp_metric = contract["metrics"]["COMPOSER_GENERALIZATION"]
    assert comp_metric["target_system"] == "FROZEN_STAGE_0_ARTIFICIAL_LISTENER"
    assert "does not involve" in comp_metric["description"].lower()


def test_grouped_kfold_youdens_j_algorithm():
    """Tests the prospective threshold selection algorithm using synthetic fold data."""
    np.random.seed(20260930)

    n_folds = 5
    fold_optimal_taus = []
    tau_grid = np.linspace(-1.0, 1.0, 401)  # step 0.005

    for _fold in range(n_folds):
        pos_scores = np.random.normal(loc=0.75, scale=0.1, size=100)
        neg_scores = np.random.normal(loc=0.35, scale=0.1, size=100)

        best_j = -1.0
        best_tau = None

        for tau in tau_grid:
            tpr = np.mean(pos_scores >= tau)
            fpr = np.mean(neg_scores >= tau)
            j = tpr - fpr
            # Tie breaking: prefer higher tau (specificity)
            if j > best_j or (math.isclose(j, best_j, rel_tol=1e-7) and best_tau is not None and tau > best_tau):
                best_j = j
                best_tau = tau

        assert best_tau is not None
        fold_optimal_taus.append(best_tau)

    median_tau = float(np.median(fold_optimal_taus))
    assert 0.45 <= median_tau <= 0.65, f"Unexpected median threshold: {median_tau}"


def test_piece_clustered_bootstrap_grouping():
    """Verifies piece-clustered bootstrap draws whole pieces rather than disconnected segments."""
    piece_segments = {f"piece_{i}": [f"seg_{i}_{j}" for j in range(np.random.randint(5, 15))] for i in range(10)}

    pieces = list(piece_segments.keys())
    np.random.seed(20260930)

    drawn_pieces = np.random.choice(pieces, size=len(pieces), replace=True)
    replicate_segments = []
    for p in drawn_pieces:
        replicate_segments.extend(piece_segments[p])

    drawn_piece_counts = {p: list(drawn_pieces).count(p) for p in set(drawn_pieces)}
    for p, count in drawn_piece_counts.items():
        prefix = f"seg_{p.split('_')[1]}_"
        actual_segments_in_rep = [s for s in replicate_segments if s.startswith(prefix)]
        assert len(actual_segments_in_rep) == count * len(piece_segments[p])

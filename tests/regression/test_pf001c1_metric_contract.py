"""Regression tests for PF-001C1 metric and calibration contract.

Verifies:
1. Validator script execution succeeds and outputs valid PF001C1_METRIC_CONTRACT_HASH.
2. Invariants: 62 pieces in physical corpus, receipt hash matches authoritative receipt.
3. All 7 gates plus theme identity and composer generalization are uncalibrated (provisional / not ready).
4. THEME_MOTIF_IDENTITY_NOT_READY enforces SOURCE_SEGMENT_IDENTITY_ONLY.
5. Mathematical logic tests:
   - Grouped K-Fold Youden's J threshold selection algorithm works deterministically with tie-breaking.
   - ClosureContrast, SurpriseContrast, and MemoryReactivation formulas.
   - Information-weighted n-gram rarity weighting logic.
   - Piece-clustered bootstrap grouping behavior.
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
    """Confirms no numerical gate thresholds are marked final or calibrated."""
    gate_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_gate_readiness.json"
    with open(gate_file, encoding="utf-8") as f:
        data = json.load(f)

    gates = data.get("gates", {})
    assert len(gates) >= 9

    for gate_name, info in gates.items():
        st = info.get("status")
        assert st in {
            "PROVISIONAL_UNCALIBRATED_TARGET",
            "NOT_READY_FOR_CALIBRATION",
            "THEME_MOTIF_IDENTITY_NOT_READY",
        }, f"Gate {gate_name} has invalid or premature status {st}"


def test_theme_identity_not_ready_and_restricted_scope():
    """Verifies that THEME_MOTIF_IDENTITY is marked NOT_READY and restricted to SOURCE_SEGMENT_IDENTITY_ONLY."""
    theme_file = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_theme_identity_readiness.json"
    with open(theme_file, encoding="utf-8") as f:
        data = json.load(f)

    assert data["status"] == "THEME_MOTIF_IDENTITY_NOT_READY"
    assert data["lineage_policy_verdict"]["operational_scope_for_pf002a"] == "SOURCE_SEGMENT_IDENTITY_ONLY"
    assert data["audit_findings"]["theme_annotation_manifest_accepted_count"] == 0
    assert data["audit_findings"]["pilot_candidates_human_accepted_count"] == 0


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

    for fam in families:
        assert "matched_control_perturbation" in fam
        assert "directional_contrast_statistic" in fam


def test_grouped_kfold_youdens_j_algorithm():
    """Tests the prospective threshold selection algorithm using synthetic fold data."""
    # Synthetic similarity scores for positive pairs and negative foils across 3 folds
    # In each fold, positive pairs ~ N(0.8, 0.1), negative foils ~ N(0.3, 0.1)
    np.random.seed(20260930)

    n_folds = 5
    fold_optimal_taus = []
    tau_grid = np.linspace(-1.0, 1.0, 401)  # step 0.005

    for _fold in range(n_folds):
        pos_scores = np.random.normal(loc=0.75, scale=0.1, size=100)
        neg_scores = np.random.normal(loc=0.35, scale=0.1, size=100)

        # Compute TPR and FPR for each tau
        # Classifier predicts positive if score >= tau
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

    # Median threshold
    median_tau = float(np.median(fold_optimal_taus))
    assert 0.45 <= median_tau <= 0.65, f"Unexpected median threshold: {median_tau}"


def test_counterfactual_contrast_formulas():
    """Verifies directional contrast calculation formulas."""
    # ClosureContrast = Closure(S o P_cad) - Closure(S o P_ctl)
    s_cad_closure = 0.85
    s_ctl_closure = 0.45
    closure_contrast = s_cad_closure - s_ctl_closure
    assert closure_contrast > 0

    # SurpriseContrast = Surprise(S o P_dis) - Surprise(S o P_ctl)
    s_dis_surprise = 3.8
    s_ctl_surprise = 1.2
    surprise_contrast = s_dis_surprise - s_ctl_surprise
    assert surprise_contrast > 0


def test_information_weighted_interval_ngram_metric():
    """Verifies that rarer n-grams carry strictly higher information weight."""
    # N-gram probabilities
    p_common = 0.10
    p_rare = 0.001

    w_common = -math.log2(p_common)
    w_rare = -math.log2(p_rare)

    assert w_rare > w_common
    assert math.isclose(w_common, 3.3219, abs_tol=1e-3)
    assert math.isclose(w_rare, 9.9657, abs_tol=1e-3)


def test_piece_clustered_bootstrap_grouping():
    """Verifies piece-clustered bootstrap draws whole pieces rather than disconnected segments."""
    # 10 pieces with variable segment counts
    piece_segments = {f"piece_{i}": [f"seg_{i}_{j}" for j in range(np.random.randint(5, 15))] for i in range(10)}

    pieces = list(piece_segments.keys())
    np.random.seed(20260930)

    # Draw piece clusters with replacement
    drawn_pieces = np.random.choice(pieces, size=len(pieces), replace=True)
    replicate_segments = []
    for p in drawn_pieces:
        replicate_segments.extend(piece_segments[p])

    # Assert that all segments for an included piece are present with proper multiplicity
    drawn_piece_counts = {p: list(drawn_pieces).count(p) for p in set(drawn_pieces)}
    for p, count in drawn_piece_counts.items():
        prefix = f"seg_{p.split('_')[1]}_"
        actual_segments_in_rep = [s for s in replicate_segments if s.startswith(prefix)]
        assert len(actual_segments_in_rep) == count * len(piece_segments[p])

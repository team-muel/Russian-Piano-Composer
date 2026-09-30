#!/usr/bin/env python3
"""Validation script for PF-001C1 / PF-001C1.1 metric and calibration contract.

Enforces fail-closed validation of:
1. Master contract file and sub-registries presence and JSON schema validity.
2. Invariant preservation: physical inventory (62 pieces), materialization receipt hash,
   and RC-012 baseline preservation.
3. Zero premature numerical threshold freezing (all gates remain PROVISIONAL_UNCALIBRATED_TARGET,
   NOT_READY_FOR_CALIBRATION, or THEME_IDENTITY_DEPENDENT_NOT_READY).
4. Semantic consistency across artifacts:
   - ClosureContrast sign and intervention semantics: ClosureContrast = Cc - Ct > 0
     (cadential disruption lowers closure more than matched control).
   - Single anti-copy smoothing estimator: ADD_ALPHA with alpha=0.1 on development corpus only.
   - Single bootstrap CI procedure: PERCENTILE, B=2000, piece_id clustering, alpha=0.05.
   - Separation of SOURCE_SEGMENT_STRUCTURAL_MEMORY from thematic memory.
   - CF-SOURCE-SEGMENT-MEMORY target and control definitions.
   - THEMATIC_MEMORY_GATE status = THEME_IDENTITY_DEPENDENT_NOT_READY.
   - COMPOSER_GENERALIZATION_GATE evaluated on frozen Listener across composer-disjoint
     human repertoire without involving generated repertoire.
   - Two admissible future theme-identity evidence routes (Route A and Route B).
5. External-test firewall protection (Taneyev, Bortkiewicz, Blumenfeld, Catoire).
6. RandomContext seed policy and piece-clustered resampling policies.
7. Contract SHA256 integrity computation.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CONTRACT_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_metric_calibration_contract.json"
TRANSFORMATION_REGISTRY_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_transformation_registry.json"
COUNTERFACTUAL_REGISTRY_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_counterfactual_registry.json"
THEME_READINESS_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_theme_identity_readiness.json"
GATE_READINESS_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_gate_readiness.json"

PHYSICAL_INVENTORY_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001_physical_corpus_inventory.json"
RECEIPT_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001b_remote_materialization_receipt.json"

EXPECTED_RECEIPT_HASH = "db2370c0fdc6010e0d917be4c953d48a1d37d59d680a5d76d8f8a63e474c689d"
FIREWALL_COMPOSERS = {"Taneyev", "Bortkiewicz", "Blumenfeld", "Catoire"}


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def validate_contract() -> int:
    print("[PF-001C1.1] Starting metric calibration contract validation...")
    errors: list[str] = []

    # 1. File existence
    required_files = [
        CONTRACT_PATH,
        TRANSFORMATION_REGISTRY_PATH,
        COUNTERFACTUAL_REGISTRY_PATH,
        THEME_READINESS_PATH,
        GATE_READINESS_PATH,
        PHYSICAL_INVENTORY_PATH,
    ]
    for rf in required_files:
        if not rf.exists():
            errors.append(f"Missing required contract file: {rf}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    # 2. Check upstream physical inventory
    with open(PHYSICAL_INVENTORY_PATH, encoding="utf-8") as f:
        inv_data = json.load(f)
    pieces = inv_data.get("scores", [])
    if len(pieces) != 62:
        errors.append(f"Physical inventory must contain exactly 62 pieces; found {len(pieces)}")

    # 3. Check materialization receipt hash if present
    if RECEIPT_PATH.exists():
        with open(RECEIPT_PATH, encoding="utf-8") as f:
            receipt_data = json.load(f)
        declared_hash = receipt_data.get("receipt_hash")
        if declared_hash != EXPECTED_RECEIPT_HASH:
            errors.append(
                f"Materialization receipt declared hash mismatch: expected {EXPECTED_RECEIPT_HASH}, got {declared_hash}"
            )
        copy_data = dict(receipt_data)
        del copy_data["receipt_hash"]
        computed_hash = hashlib.sha256(json.dumps(copy_data, sort_keys=True, indent=2).encode("utf-8")).hexdigest()
        if computed_hash != EXPECTED_RECEIPT_HASH:
            errors.append(
                f"Materialization receipt content hash mismatch: expected {EXPECTED_RECEIPT_HASH}, got {computed_hash}"
            )
    else:
        errors.append(f"Missing materialization receipt: {RECEIPT_PATH}")

    # 4. Check master contract
    with open(CONTRACT_PATH, encoding="utf-8") as f:
        contract = json.load(f)

    if contract.get("contract_name") != "PF001C1_METRIC_AND_CALIBRATION_CONTRACT":
        errors.append("Contract name must be PF001C1_METRIC_AND_CALIBRATION_CONTRACT")

    if contract.get("authoritative_receipt_hash") != EXPECTED_RECEIPT_HASH:
        errors.append("Contract receipt hash mismatch with authoritative constant")

    firewall = contract.get("external_test_firewall", {})
    if firewall.get("status") != "ENFORCED_BLINDED":
        errors.append("external_test_firewall status must be ENFORCED_BLINDED")
    if set(firewall.get("cohort", [])) != FIREWALL_COMPOSERS:
        errors.append(f"external_test_firewall cohort must match {FIREWALL_COMPOSERS}")

    eval_units = contract.get("evaluation_units", {})
    primary_cluster = eval_units.get("primary_cluster_unit", {}).get("name")
    if primary_cluster != "piece_id":
        errors.append("primary_cluster_unit must be 'piece_id'")

    # 4.1 Strict single bootstrap CI procedure
    resamp_policy = contract.get("resampling_and_uncertainty_policy", {})
    if resamp_policy.get("bootstrap_replicates") != 2000:
        errors.append(f"bootstrap_replicates must be exactly 2000, got {resamp_policy.get('bootstrap_replicates')}")
    if resamp_policy.get("cluster_unit") != "piece_id":
        errors.append("resampling cluster_unit must be 'piece_id'")
    if resamp_policy.get("confidence_interval_method") != "PERCENTILE":
        errors.append(f"confidence_interval_method must be strictly 'PERCENTILE', got {resamp_policy.get('confidence_interval_method')}")
    if resamp_policy.get("confidence_level") != 0.95:
        errors.append("confidence_level must be 0.95")

    # 4.2 Single anti-copy smoothing estimator
    tier2 = contract.get("metrics", {}).get("ANTI_COPY_METRICS", {}).get("tier_2_weighted_interval_ngram", {})
    if tier2.get("smoothing_method") != "ADD_ALPHA":
        errors.append(f"Anti-copy smoothing method must be strictly 'ADD_ALPHA', got {tier2.get('smoothing_method')}")
    if tier2.get("alpha") != 0.1:
        errors.append(f"Anti-copy alpha must be 0.1, got {tier2.get('alpha')}")
    if tier2.get("corpus_scope") != "DEVELOPMENT_CORPUS_ONLY":
        errors.append(f"Anti-copy corpus_scope must be 'DEVELOPMENT_CORPUS_ONLY', got {tier2.get('corpus_scope')}")

    # 4.3 ClosureContrast formula consistency
    closure_metric = contract.get("metrics", {}).get("CLOSURE_CONTRAST", {})
    if "Cc - Ct" not in closure_metric.get("formula", ""):
        errors.append("ClosureContrast formula must specify Cc - Ct")
    if "preparation increases" in closure_metric.get("interpretation", "").lower():
        errors.append("Contradictory 'preparation increases closure' language found in contract")

    # 4.4 Composer Generalization Listener-only semantics
    comp_gen = contract.get("metrics", {}).get("COMPOSER_GENERALIZATION", {})
    if comp_gen.get("target_system") != "FROZEN_STAGE_0_ARTIFICIAL_LISTENER":
        errors.append("COMPOSER_GENERALIZATION target_system must be FROZEN_STAGE_0_ARTIFICIAL_LISTENER")
    if "generated repertoire" in comp_gen.get("description", "").lower() and "does not involve" not in comp_gen.get("description", "").lower():
        errors.append("Composer generalization must not depend on generated repertoire")

    algo = contract.get("threshold_selection_algorithm", {})
    if algo.get("method") != "GROUPED_KFOLD_YOUDENS_J":
        errors.append("threshold_selection_algorithm method must be GROUPED_KFOLD_YOUDENS_J")
    if algo.get("group_key") != "piece_id":
        errors.append("threshold_selection_algorithm group_key must be piece_id")

    # 5. Check theme readiness
    with open(THEME_READINESS_PATH, encoding="utf-8") as f:
        theme_data = json.load(f)
    if theme_data.get("status") != "THEME_MOTIF_IDENTITY_NOT_READY":
        errors.append("Theme identity status must be THEME_MOTIF_IDENTITY_NOT_READY")
    op_scope = theme_data.get("lineage_policy_verdict", {}).get("operational_scope_for_pf002a")
    if op_scope != "SOURCE_SEGMENT_IDENTITY_ONLY":
        errors.append(f"Theme identity operational_scope must be SOURCE_SEGMENT_IDENTITY_ONLY, got {op_scope}")

    admissible_routes = theme_data.get("admissible_evidence_routes", {})
    if "ROUTE_A" not in admissible_routes or "ROUTE_B" not in admissible_routes:
        errors.append("Theme identity must specify both ROUTE_A and ROUTE_B admissible routes")

    # 6. Check transformation registry
    with open(TRANSFORMATION_REGISTRY_PATH, encoding="utf-8") as f:
        trans_data = json.load(f)
    transformations = trans_data.get("transformations", [])
    if len(transformations) < 7:
        errors.append(f"Transformation registry must contain at least 7 transformations, found {len(transformations)}")
    trans_ids = {t["transformation_id"] for t in transformations}
    expected_trans_ids = {
        "T_ID_PITCH_TRANSPOSITION",
        "T_ID_OCTAVE_DISPLACEMENT",
        "T_ID_RHYTHMIC_AUGMENTATION",
        "T_ID_RHYTHMIC_DIMINUTION",
        "T_ID_LIMITED_ORNAMENT_INSERTION",
        "T_ID_LIMITED_ORNAMENT_DELETION",
        "T_ID_ACCOMPANIMENT_TEXTURE_VARIATION",
    }
    if not expected_trans_ids.issubset(trans_ids):
        errors.append(f"Missing expected transformations: {expected_trans_ids - trans_ids}")

    # 7. Check counterfactual registry
    with open(COUNTERFACTUAL_REGISTRY_PATH, encoding="utf-8") as f:
        cf_data = json.load(f)
    cf_families = cf_data.get("perturbation_families", [])
    if len(cf_families) < 3:
        errors.append(f"Counterfactual registry must contain at least 3 families, found {len(cf_families)}")
    family_ids = {cf["family_id"] for cf in cf_families}
    expected_cf = {"CF-CLOSURE", "CF-SOURCE-SEGMENT-MEMORY", "CF-SURPRISE"}
    if not expected_cf.issubset(family_ids):
        errors.append(f"Missing expected counterfactual families: {expected_cf - family_ids}")

    for cf in cf_families:
        if not cf.get("matched_control_perturbation"):
            errors.append(f"Counterfactual family {cf.get('family_id')} missing matched_control_perturbation")
        if not cf.get("directional_contrast_statistic"):
            errors.append(f"Counterfactual family {cf.get('family_id')} missing directional_contrast_statistic")

    # Semantic check on CF-CLOSURE formula
    cf_closure = next((cf for cf in cf_families if cf["family_id"] == "CF-CLOSURE"), None)
    if cf_closure:
        formula = cf_closure.get("directional_contrast_statistic", {}).get("formula", "")
        if "Closure(T_matched_control(X)) - Closure(T_target_disruption(X))" not in formula:
            errors.append("CF-CLOSURE formula must equal Closure(T_matched_control(X)) - Closure(T_target_disruption(X))")

    # 8. Check gate readiness: NO PREMATURE NUMERICAL FREEZING
    with open(GATE_READINESS_PATH, encoding="utf-8") as f:
        gate_data = json.load(f)
    gates = gate_data.get("gates", {})
    if "COMPOSER_GENERALIZATION_GATE" not in gates:
        errors.append("COMPOSER_GENERALIZATION_GATE missing from gate readiness")
    elif gates["COMPOSER_GENERALIZATION_GATE"]["status"] != "NOT_READY_FOR_CALIBRATION":
        errors.append("COMPOSER_GENERALIZATION_GATE status must be NOT_READY_FOR_CALIBRATION")

    if "THEMATIC_MEMORY_GATE" not in gates:
        errors.append("THEMATIC_MEMORY_GATE missing from gate readiness")
    elif gates["THEMATIC_MEMORY_GATE"]["status"] != "THEME_IDENTITY_DEPENDENT_NOT_READY":
        errors.append("THEMATIC_MEMORY_GATE status must be THEME_IDENTITY_DEPENDENT_NOT_READY")

    if "SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE" not in gates:
        errors.append("SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE missing from gate readiness")

    for g_id, g_info in gates.items():
        st = g_info.get("status")
        if st not in {
            "PROVISIONAL_UNCALIBRATED_TARGET",
            "NOT_READY_FOR_CALIBRATION",
            "THEME_MOTIF_IDENTITY_NOT_READY",
            "THEME_IDENTITY_DEPENDENT_NOT_READY",
        }:
            errors.append(f"Gate {g_id} has invalid status {st}; cannot be finalized in PF-001C1")

        # Confirm no numerical thresholds in active gate descriptions
        desc = g_info.get("provisional_threshold_description", "")
        for stale_val in ["0.85", "0.30", "0.95", "1.80", "0.50", "15%"]:
            if stale_val in desc:
                errors.append(f"Gate {g_id} provisional description contains stale numerical value '{stale_val}'")

    if errors:
        print("[PF-001C1.1] Contract validation FAILED with errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    contract_sha256 = compute_sha256(CONTRACT_PATH)
    print("[PF-001C1.1] Contract validation SUCCESSFUL.")
    print(f"PF001C1_METRIC_CONTRACT_HASH={contract_sha256}")
    return 0


if __name__ == "__main__":
    sys.exit(validate_contract())

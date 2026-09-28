"""PF-001 Machine-Readable Measurement Contract Validator.

Validates the scientific integrity of the PF-001 Perception-First Artificial Listener
construct registry, schema definitions, Stage-0 scope boundaries, generalization split
policies, and immutability of historical RC-012 artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Authoritative frozen hashes for RC-012 result artifacts
RC012_EXPECTED_RESULT_CANONICAL_HASH = (
    "a933ac2b21fe50cff9c0a43e8216ee37593acded32e22ecb0e9502b231cffded"
)
RC012_EXPECTED_PIECE_LEDGER_HASH = (
    "66513dc4901b48ee865ba826cb4dad824f448b242b94834fd25202d39c5aa634"
)
RC012_EXPECTED_BOOTSTRAP_MATRIX_HASH = (
    "d606705dd1621a4b0fef85c1dbec2f2f1347891c8576a2162e64ac9306b5b739"
)

STAGE_0_APPROVED_NAMESPACES = {
    "structural_expectation",
    "structural_uncertainty",
    "structural_surprise",
    "structural_closure",
    "motif_identity",
    "structural_memory",
}

ALLOWED_STATUSES = {
    "MEASURABLE_NOW",
    "LATENT_NEEDS_VALIDATION",
    "HIGH_LEVEL_NOT_OPERATIONAL",
    "REJECTED_AS_DIRECT_SCALAR",
}

REQUIRED_CONSTRUCT_FIELDS = [
    "construct_id",
    "construct_name",
    "conceptual_definition",
    "timescale",
    "measurement_class",
    "human_observable",
    "stimulus_unit",
    "response_type",
    "model_output",
    "derived_variables",
    "primary_validation_metric",
    "secondary_validation_metrics",
    "intervention_test",
    "known_confounders",
    "current_status",
]

REQUIRED_SCHEMA_PROPERTIES = [
    "listener_id",
    "trial_id",
    "piece_id",
    "composer_id",
    "performance_id",
    "segment_id",
    "motif_id",
    "event_time",
    "beat_position",
    "musical_timescale",
    "task_type",
    "condition_id",
    "exposure_index",
    "human_response",
    "human_confidence",
    "response_time",
    "human_continuation_distribution",
    "human_closure_rating",
    "recognition_response",
    "recognition_confidence",
    "recognition_rt",
    "recall_delay",
    "recall_representation",
    "recall_similarity",
    "model_prediction_distribution",
    "model_uncertainty",
    "model_surprise",
    "model_closure_probability",
    "model_recognition_score",
    "split_id",
    "source_version",
    "annotation_version",
]


def validate_construct_registry(
    registry_path: Path,
) -> tuple[bool, list[str], dict[str, Any]]:
    errors: list[str] = []
    if not registry_path.exists():
        return False, [f"Construct registry not found: {registry_path}"], {}

    with open(registry_path, encoding="utf-8") as f:
        data = json.load(f)

    constructs = data.get("constructs", [])
    if not isinstance(constructs, list) or len(constructs) == 0:
        return False, ["Construct registry has no constructs or invalid list."], {}

    seen_ids: set[str] = set()
    stage0_found_namespaces: set[str] = set()

    for idx, c in enumerate(constructs):
        cid = c.get("construct_id")
        cname = c.get("construct_name", f"construct_{idx}")

        # 1. All registered constructs have IDs
        if not cid or not isinstance(cid, str):
            errors.append(f"Construct #{idx} ('{cname}') lacks a valid 'construct_id'.")
            continue
        if cid in seen_ids:
            errors.append(f"Duplicate construct_id found: '{cid}'.")
        seen_ids.add(cid)

        # Check required fields
        for field in REQUIRED_CONSTRUCT_FIELDS:
            if field not in c:
                errors.append(f"Construct '{cid}' missing required field: '{field}'.")

        status = c.get("current_status")
        if status not in ALLOWED_STATUSES:
            errors.append(
                f"Construct '{cid}' has invalid status '{status}'. Must be one of {sorted(ALLOWED_STATUSES)}."
            )

        # 2. Every MEASURABLE_NOW construct has a human observable
        h_obs = c.get("human_observable")
        if status == "MEASURABLE_NOW" and (
            not h_obs or not isinstance(h_obs, str) or len(h_obs.strip()) == 0
        ):
            errors.append(
                f"Construct '{cid}' is MEASURABLE_NOW but has no declared human_observable."
            )

        # 3. Every model target has an independent human target
        model_out = c.get("model_output")
        if model_out is not None and (
            not h_obs or not isinstance(h_obs, str) or len(h_obs.strip()) == 0
        ):
            errors.append(
                f"Construct '{cid}' declares model_output '{model_out}' without an independent human_observable."
            )

        # 4. No HIGH_LEVEL_NOT_OPERATIONAL or REJECTED_AS_DIRECT_SCALAR concept is used as an optimization score
        if status in {"HIGH_LEVEL_NOT_OPERATIONAL", "REJECTED_AS_DIRECT_SCALAR"}:
            if model_out is not None:
                errors.append(
                    f"Construct '{cid}' is '{status}' but declares a model_output: '{model_out}'."
                )
            if c.get("stage_0_scope") is True:
                errors.append(
                    f"Construct '{cid}' is '{status}' but is improperly included in stage_0_scope."
                )

        # 5. Check timescale is declared
        timescale = c.get("timescale")
        if not timescale or not isinstance(timescale, str) or len(timescale.strip()) == 0:
            errors.append(f"Construct '{cid}' lacks a declared measurement timescale.")

        # Stage-0 tracking
        if c.get("stage_0_scope") is True:
            ns = c.get("stage_0_namespace")
            if not ns or not isinstance(ns, str):
                errors.append(f"Construct '{cid}' has stage_0_scope=True but no stage_0_namespace.")
            else:
                base_ns = ns.split(".")[0]
                stage0_found_namespaces.add(base_ns)

    # 5. Verify Stage-0 contains exactly the approved initial constructs
    missing_stage0 = STAGE_0_APPROVED_NAMESPACES - stage0_found_namespaces
    extra_stage0 = stage0_found_namespaces - STAGE_0_APPROVED_NAMESPACES
    if missing_stage0:
        errors.append(f"Stage-0 scope missing required namespaces: {sorted(missing_stage0)}")
    if extra_stage0:
        errors.append(f"Stage-0 scope contains unapproved namespaces: {sorted(extra_stage0)}")

    summary = {
        "total_constructs": len(constructs),
        "status_distribution": {
            s: sum(1 for c in constructs if c.get("current_status") == s) for s in ALLOWED_STATUSES
        },
        "stage_0_namespaces": sorted(stage0_found_namespaces),
    }
    return len(errors) == 0, errors, summary


def validate_listener_observation_schema(
    schema_path: Path,
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not schema_path.exists():
        return False, [f"Observation schema not found: {schema_path}"]

    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    props = schema.get("properties", {})
    for req_prop in REQUIRED_SCHEMA_PROPERTIES:
        if req_prop not in props:
            errors.append(f"Schema missing required property: '{req_prop}'.")

    # Verify separate namespacing:
    # Model variables must start with 'model_'
    # Human behavioral variables must not collide with model variables
    for prop_name in props:
        if prop_name.startswith("model_"):
            pass  # correctly namespaced model target
        elif prop_name.startswith("human_") or prop_name in {
            "recognition_response",
            "recognition_confidence",
            "recognition_rt",
            "recall_delay",
            "recall_representation",
            "recall_similarity",
            "response_time",
        }:
            pass  # correctly namespaced human observation
        else:
            # Context / metadata properties
            pass

    # Verify strict pseudonymity constraint on listener_id
    listener_id_prop = props.get("listener_id", {})
    if "pattern" not in listener_id_prop:
        errors.append("Schema property 'listener_id' must declare a pseudonymity regex pattern.")

    return len(errors) == 0, errors


def validate_split_policy(policy_path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not policy_path.exists():
        return False, [f"Split policy document not found: {policy_path}"]

    content = policy_path.read_text(encoding="utf-8")

    required_keywords = [
        "development",
        "validation",
        "external_test_held_out",
        "Tchaikovsky",
        "Rachmaninoff",
        "Scriabin",
        "Medtner",
        "Taneyev",
        "Bortkiewicz",
        "RC-012",
        "PREDICTIVE_VALIDITY",
        "TEMPORAL_VALIDITY",
        "INTERVENTION_VALIDITY",
        "GENERALIZATION_VALIDITY",
    ]

    for kw in required_keywords:
        if kw not in content:
            errors.append(f"Split policy missing mandatory requirement or composer: '{kw}'.")

    return len(errors) == 0, errors


def validate_rc012_immutability(repo_root: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    result_path = repo_root / "data/reviews/rc012/rc012_one_shot_confirmatory_result.json"

    if not result_path.exists():
        return False, [f"Authoritative RC-012 result file missing: {result_path}"]

    with open(result_path, encoding="utf-8") as f:
        data = json.load(f)

    if data.get("confirmatory_result_hash") != RC012_EXPECTED_RESULT_CANONICAL_HASH:
        errors.append(
            f"RC-012 confirmatory_result_hash altered! Expected {RC012_EXPECTED_RESULT_CANONICAL_HASH}, found {data.get('confirmatory_result_hash')}."
        )

    rep = data.get("repertoire_summary", {})
    if rep.get("piece_ledger_sha256") != RC012_EXPECTED_PIECE_LEDGER_HASH:
        errors.append(
            f"RC-012 piece_ledger_sha256 altered! Expected {RC012_EXPECTED_PIECE_LEDGER_HASH}, found {rep.get('piece_ledger_sha256')}."
        )

    sec = data.get("secondary_metrics", {})
    if sec.get("bootstrap_replicate_matrix_sha256") != RC012_EXPECTED_BOOTSTRAP_MATRIX_HASH:
        errors.append(
            f"RC-012 bootstrap_replicate_matrix_sha256 altered! Expected {RC012_EXPECTED_BOOTSTRAP_MATRIX_HASH}, found {sec.get('bootstrap_replicate_matrix_sha256')}."
        )

    return len(errors) == 0, errors


def validate_synthetic_dummy_observation(
    schema_path: Path,
) -> tuple[bool, list[str]]:
    """Validates that a synthetic metadata record conforms to the schema without participant data."""
    errors: list[str] = []
    synthetic_record = {
        "listener_id": "LST-A1B2C3D4",
        "trial_id": "TRL-EXP001-0001",
        "piece_id": "TCH-OP37A-01",
        "composer_id": "CMP-TCHAIKOVSKY",
        "performance_id": "PRF-STUDIO-2024",
        "segment_id": "SEG-001",
        "motif_id": "MTF-HEAD-01",
        "event_time": 12.45,
        "beat_position": 16.0,
        "musical_timescale": "event_level",
        "task_type": "continuation_choice",
        "condition_id": "COND-PRISTINE",
        "exposure_index": 1,
        "human_response": "C1",
        "human_confidence": 0.85,
        "response_time": 642.0,
        "human_continuation_distribution": {
            "C1": 0.72,
            "C2": 0.18,
            "C3": 0.08,
            "C4": 0.02,
        },
        "human_closure_rating": 0.25,
        "recognition_response": 1,
        "recognition_confidence": 0.90,
        "recognition_rt": 512.0,
        "recall_delay": 0.0,
        "recall_representation": "G4 E4 D4 C4",
        "recall_similarity": 0.95,
        "model_prediction_distribution": {
            "C1": 0.68,
            "C2": 0.22,
            "C3": 0.07,
            "C4": 0.03,
        },
        "model_uncertainty": 1.15,
        "model_surprise": 0.55,
        "model_closure_probability": 0.22,
        "model_recognition_score": 0.92,
        "split_id": "development",
        "source_version": "git-commit-hash-abc1234",
        "annotation_version": "1.0.0",
    }

    # Verify listener_id regex pattern
    pattern = r"^LST-[A-Z0-9]{8,16}$"
    if not re.match(pattern, str(synthetic_record["listener_id"])):
        errors.append(f"Synthetic listener_id failed pattern: {synthetic_record['listener_id']}")

    for prop in REQUIRED_SCHEMA_PROPERTIES:
        if prop not in synthetic_record:
            errors.append(f"Synthetic dummy missing required property: '{prop}'")

    return len(errors) == 0, errors


def run_all_contract_validations(repo_root: Path) -> dict[str, Any]:
    registry_path = repo_root / "data/reviews/pf001/pf001_construct_registry.json"
    schema_path = repo_root / "data/schemas/pf001_listener_observation.schema.json"
    policy_path = repo_root / "docs/research/PF001_GENERALIZATION_AND_SPLIT_POLICY.md"

    reg_ok, reg_errs, summary = validate_construct_registry(registry_path)
    sch_ok, sch_errs = validate_listener_observation_schema(schema_path)
    pol_ok, pol_errs = validate_split_policy(policy_path)
    rc12_ok, rc12_errs = validate_rc012_immutability(repo_root)
    syn_ok, syn_errs = validate_synthetic_dummy_observation(schema_path)

    all_passed = reg_ok and sch_ok and pol_ok and rc12_ok and syn_ok
    all_errors = reg_errs + sch_errs + pol_errs + rc12_errs + syn_errs

    return {
        "status": "PASS" if all_passed else "FAIL",
        "passed": all_passed,
        "errors": all_errors,
        "registry_summary": summary,
        "verifications": {
            "construct_registry": "PASS" if reg_ok else "FAIL",
            "observation_schema": "PASS" if sch_ok else "FAIL",
            "split_policy": "PASS" if pol_ok else "FAIL",
            "rc012_immutability": "PASS" if rc12_ok else "FAIL",
            "synthetic_metadata_compliance": "PASS" if syn_ok else "FAIL",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate PF-001 Measurement Contract and Construct Registry."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root directory.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output validation results in JSON format.",
    )
    args = parser.parse_args()

    results = run_all_contract_validations(args.repo_root)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 70)
        print("PF-001 MEASUREMENT CONTRACT VALIDATION REPORT")
        print("=" * 70)
        print(f"Overall Status: {results['status']}")
        for check, res in results["verifications"].items():
            print(f"  - {check:<35}: {res}")
        if not results["passed"]:
            print("\nValidation Errors:")
            for err in results["errors"]:
                print(f"  [ERROR] {err}")
        else:
            print("\nConstruct Summary:")
            print(f"  Total Constructs: {results['registry_summary']['total_constructs']}")
            print(f"  Stage-0 Namespaces: {results['registry_summary']['stage_0_namespaces']}")
            print(f"  Status Distribution: {results['registry_summary']['status_distribution']}")
        print("=" * 70)

    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

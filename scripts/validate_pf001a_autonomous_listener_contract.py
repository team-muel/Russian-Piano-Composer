"""PF-001A Autonomous Artificial Listener Contract Validator.

Validates the machine-readable requirements of PF-001A:
1. No Stage-0 structural variable requires human participant annotation.
2. Subjective-human claims remain explicitly gated with required human validation.
3. External composer split is NOT frozen before physical corpus feasibility passes.
4. RC-012 authoritative hashes remain immutable.
5. Anti-copy policy and multi-scale representations exist.
6. Counterfactual validation protocols exist.
7. Human observation schema is preserved as optional only.
8. Primary autonomous observation schema conforms to structural requirements.
"""

from __future__ import annotations

import argparse
import json
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

STAGE_0_AUTONOMOUS_NAMESPACES = {
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

ALLOWED_LEARNING_SUPERVISIONS = {
    "CORPUS_SELF_SUPERVISED",
    "CORPUS_WEAK_SUPERVISED",
    "SYMBOLIC_METADATA_SUPERVISED",
    "ACOUSTIC_SELF_SUPERVISED",
    "HUMAN_VALIDATION_OPTIONAL",
    "HUMAN_VALIDATION_REQUIRED_FOR_SUBJECTIVE_CLAIM",
    "NOT_YET_OPERATIONAL",
}

ALLOWED_CLAIM_SCOPES = {
    "STRUCTURAL",
    "PERCEPTUAL_PROXY",
    "SUBJECTIVE_HUMAN",
    "HIGH_LEVEL_OPEN",
}

REQUIRED_AUTONOMOUS_SCHEMA_PROPERTIES = [
    "piece_id",
    "composer_id",
    "source_id",
    "segment_id",
    "event_index",
    "event_time",
    "beat_position",
    "timescale",
    "input_context_span",
    "target_event",
    "target_boundary",
    "structural_expectation",
    "structural_uncertainty",
    "structural_surprise",
    "structural_closure",
    "motif_identity_score",
    "structural_memory_trace",
    "split_id",
    "corpus_version",
    "feature_version",
    "model_version",
]


def validate_pf001a_construct_registry(
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

        if not cid or not isinstance(cid, str):
            errors.append(f"Construct #{idx} ('{cname}') lacks a valid 'construct_id'.")
            continue
        if cid in seen_ids:
            errors.append(f"Duplicate construct_id found: '{cid}'.")
        seen_ids.add(cid)

        # Learning supervision & claim scope
        lsup = c.get("learning_supervision")
        if lsup not in ALLOWED_LEARNING_SUPERVISIONS:
            errors.append(
                f"Construct '{cid}' invalid learning_supervision '{lsup}'. Must be one of {sorted(ALLOWED_LEARNING_SUPERVISIONS)}."
            )

        cscope = c.get("claim_scope")
        if cscope not in ALLOWED_CLAIM_SCOPES:
            errors.append(
                f"Construct '{cid}' invalid claim_scope '{cscope}'. Must be one of {sorted(ALLOWED_CLAIM_SCOPES)}."
            )

        # Stage-0 structural gating: no Stage-0 structural variable may require human annotation
        if c.get("stage_0_scope") is True:
            if cscope != "STRUCTURAL":
                errors.append(
                    f"Stage-0 construct '{cid}' has claim_scope '{cscope}', must be 'STRUCTURAL'."
                )
            if lsup in {"HUMAN_VALIDATION_REQUIRED_FOR_SUBJECTIVE_CLAIM", "NOT_YET_OPERATIONAL"}:
                errors.append(
                    f"Stage-0 construct '{cid}' has learning_supervision '{lsup}' requiring human annotation."
                )
            ns = c.get("stage_0_namespace")
            if not ns or not isinstance(ns, str):
                errors.append(f"Stage-0 construct '{cid}' missing stage_0_namespace.")
            else:
                stage0_found_namespaces.add(ns)

        # Subjective-human claims must require human evidence
        if (
            cscope == "SUBJECTIVE_HUMAN"
            and lsup != "HUMAN_VALIDATION_REQUIRED_FOR_SUBJECTIVE_CLAIM"
        ):
            errors.append(
                f"Construct '{cid}' has claim_scope 'SUBJECTIVE_HUMAN' but does not declare HUMAN_VALIDATION_REQUIRED_FOR_SUBJECTIVE_CLAIM."
            )

        # High-level rejected scalars cannot have model output
        status = c.get("current_status")
        if status in {"HIGH_LEVEL_NOT_OPERATIONAL", "REJECTED_AS_DIRECT_SCALAR"}:
            if c.get("model_output") is not None:
                errors.append(f"Banned construct '{cid}' has non-null model_output.")
            if c.get("stage_0_scope") is True:
                errors.append(f"Banned construct '{cid}' included in Stage-0 scope.")

    # Verify Stage-0 namespaces match exactly
    missing_s0 = STAGE_0_AUTONOMOUS_NAMESPACES - stage0_found_namespaces
    extra_s0 = stage0_found_namespaces - STAGE_0_AUTONOMOUS_NAMESPACES
    if missing_s0:
        errors.append(f"Stage-0 missing autonomous namespaces: {sorted(missing_s0)}")
    if extra_s0:
        errors.append(f"Stage-0 contains unapproved namespaces: {sorted(extra_s0)}")

    summary = {
        "total_constructs": len(constructs),
        "stage_0_namespaces": sorted(stage0_found_namespaces),
        "learning_supervision_counts": {
            ls: sum(1 for c in constructs if c.get("learning_supervision") == ls)
            for ls in ALLOWED_LEARNING_SUPERVISIONS
        },
        "claim_scope_counts": {
            cs: sum(1 for c in constructs if c.get("claim_scope") == cs)
            for cs in ALLOWED_CLAIM_SCOPES
        },
    }
    return len(errors) == 0, errors, summary


def validate_pf001a_autonomous_schema(schema_path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not schema_path.exists():
        return False, [f"Autonomous schema missing: {schema_path}"]

    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    props = schema.get("properties", {})
    for req_prop in REQUIRED_AUTONOMOUS_SCHEMA_PROPERTIES:
        if req_prop not in props:
            errors.append(f"Autonomous schema missing required property: '{req_prop}'")

    # Multi-scale check: timescale enum must support event, motif, phrase, section, whole-piece
    timescale_enum = props.get("timescale", {}).get("enum", [])
    expected_scales = {"event", "motif", "phrase", "section", "whole-piece"}
    if not expected_scales.issubset(set(timescale_enum)):
        errors.append(
            f"Timescale property must include {sorted(expected_scales)}, found {timescale_enum}"
        )

    # Counterfactual check: perturbation properties must exist
    if "perturbation_type" not in props or "perturbation_strength" not in props:
        errors.append(
            "Autonomous schema missing perturbation properties for counterfactual testing."
        )

    return len(errors) == 0, errors


def validate_composer_feasibility_audit(
    feasibility_json_path: Path, feasibility_md_path: Path
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not feasibility_json_path.exists():
        return False, [f"Feasibility JSON missing: {feasibility_json_path}"]
    if not feasibility_md_path.exists():
        return False, [f"Feasibility MD report missing: {feasibility_md_path}"]

    with open(feasibility_json_path, encoding="utf-8") as f:
        data = json.load(f)

    status = data.get("status")
    if status != "PROVISIONAL_PENDING_CORPUS_FEASIBILITY_AUDIT":
        errors.append(
            f"Feasibility status must be 'PROVISIONAL_PENDING_CORPUS_FEASIBILITY_AUDIT', found '{status}'"
        )

    findings = data.get("audit_findings", {})
    if findings.get("external_test_held_out_ready") is not False:
        errors.append(
            "External test held-out cohort cannot be marked ready before physical score digitization audit passes."
        )

    cohorts = data.get("composer_cohorts", {})
    for cohort_name in ["development", "validation", "external_test_held_out"]:
        if cohort_name not in cohorts or len(cohorts[cohort_name]) == 0:
            errors.append(f"Feasibility audit missing cohort '{cohort_name}'.")

    return len(errors) == 0, errors


def validate_autonomous_contract_doc(contract_doc_path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not contract_doc_path.exists():
        return False, [f"Autonomous contract doc missing: {contract_doc_path}"]

    content = contract_doc_path.read_text(encoding="utf-8")
    required_keywords = [
        "HUMAN CLASSICAL CORPUS",
        "SELF-SUPERVISED",
        "STRUCTURAL WORLD MODEL",
        "PREDICTIVE_GATE",
        "INVARIANCE_GATE",
        "DISCRIMINATION_GATE",
        "COUNTERFACTUAL_GATE",
        "LONG_RANGE_MEMORY_GATE",
        "COMPOSER_GENERALIZATION_GATE",
        "ANTI_COPY_GATE",
        "Multi-Scale Representation Contract",
        "OPTIONAL_EXTERNAL_VALIDATION",
    ]
    for kw in required_keywords:
        if kw not in content:
            errors.append(f"Autonomous contract doc missing required specification: '{kw}'")

    return len(errors) == 0, errors


def validate_rc012_integrity_pf001a(repo_root: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    result_path = repo_root / "data/reviews/rc012/rc012_one_shot_confirmatory_result.json"

    if not result_path.exists():
        return False, [f"RC-012 result file missing: {result_path}"]

    with open(result_path, encoding="utf-8") as f:
        data = json.load(f)

    if data.get("confirmatory_result_hash") != RC012_EXPECTED_RESULT_CANONICAL_HASH:
        errors.append("RC-012 confirmatory_result_hash altered!")

    rep = data.get("repertoire_summary", {})
    if rep.get("piece_ledger_sha256") != RC012_EXPECTED_PIECE_LEDGER_HASH:
        errors.append("RC-012 piece_ledger_sha256 altered!")

    sec = data.get("secondary_metrics", {})
    if sec.get("bootstrap_replicate_matrix_sha256") != RC012_EXPECTED_BOOTSTRAP_MATRIX_HASH:
        errors.append("RC-012 bootstrap_replicate_matrix_sha256 altered!")

    return len(errors) == 0, errors


def run_all_pf001a_validations(repo_root: Path) -> dict[str, Any]:
    reg_path = repo_root / "data/reviews/pf001/pf001_construct_registry.json"
    auto_schema_path = repo_root / "data/schemas/pf001_autonomous_listener_observation.schema.json"
    feas_json = repo_root / "data/reviews/pf001/pf001_composer_corpus_feasibility.json"
    feas_md = repo_root / "docs/research/PF001_COMPOSER_CORPUS_FEASIBILITY_AUDIT.md"
    contract_doc = repo_root / "docs/research/PF001A_AUTONOMOUS_LISTENER_CONTRACT.md"

    reg_ok, reg_err, reg_sum = validate_pf001a_construct_registry(reg_path)
    sch_ok, sch_err = validate_pf001a_autonomous_schema(auto_schema_path)
    feas_ok, feas_err = validate_composer_feasibility_audit(feas_json, feas_md)
    doc_ok, doc_err = validate_autonomous_contract_doc(contract_doc)
    rc12_ok, rc12_err = validate_rc012_integrity_pf001a(repo_root)

    all_passed = reg_ok and sch_ok and feas_ok and doc_ok and rc12_ok
    all_errors = reg_err + sch_err + feas_err + doc_err + rc12_err

    return {
        "status": "PASS" if all_passed else "FAIL",
        "passed": all_passed,
        "errors": all_errors,
        "summary": reg_sum,
        "verifications": {
            "construct_registry_pf001a": "PASS" if reg_ok else "FAIL",
            "autonomous_observation_schema": "PASS" if sch_ok else "FAIL",
            "composer_corpus_feasibility": "PASS" if feas_ok else "FAIL",
            "autonomous_contract_doc": "PASS" if doc_ok else "FAIL",
            "rc012_immutability": "PASS" if rc12_ok else "FAIL",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate PF-001A Autonomous Listener Contract & Feasibility."
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
        help="Output in JSON format.",
    )
    args = parser.parse_args()

    results = run_all_pf001a_validations(args.repo_root)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 70)
        print("PF-001A AUTONOMOUS LISTENER CONTRACT VALIDATION REPORT")
        print("=" * 70)
        print(f"Overall Status: {results['status']}")
        for check, res in results["verifications"].items():
            print(f"  - {check:<35}: {res}")
        if not results["passed"]:
            print("\nErrors:")
            for err in results["errors"]:
                print(f"  [ERROR] {err}")
        else:
            print("\nRegistry Summary:")
            print(f"  Total Constructs: {results['summary']['total_constructs']}")
            print(f"  Stage-0 Namespaces: {results['summary']['stage_0_namespaces']}")
            print(f"  Learning Supervision: {results['summary']['learning_supervision_counts']}")
            print(f"  Claim Scopes: {results['summary']['claim_scope_counts']}")
        print("=" * 70)

    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

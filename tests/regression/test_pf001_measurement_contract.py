"""PF-001 / PF-001A Measurement & Autonomous Contract Regression Test Suite.

Verifies:
1. Human participant data is NOT required for Stage-0 training or validation.
2. Structural and subjective-human variables cannot be conflated.
3. High-level quality scalars remain strictly prohibited.
4. Provisional composer cohorts cannot become FROZEN without feasibility audit PASS.
5. RC-012 artifacts and result hashes remain strictly immutable.
6. Autonomous scientific gates, anti-copy policy, and multi-scale representations exist.
7. Both autonomous and optional human observation schemas validate properly.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_pf001_measurement_contract import (
    ALLOWED_STATUSES,
    RC012_EXPECTED_BOOTSTRAP_MATRIX_HASH,
    RC012_EXPECTED_PIECE_LEDGER_HASH,
    RC012_EXPECTED_RESULT_CANONICAL_HASH,
    REQUIRED_CONSTRUCT_FIELDS,
    REQUIRED_SCHEMA_PROPERTIES,
    STAGE_0_APPROVED_NAMESPACES,
    run_all_contract_validations,
    validate_rc012_immutability,
)
from scripts.validate_pf001a_autonomous_listener_contract import (
    ALLOWED_CLAIM_SCOPES,
    ALLOWED_LEARNING_SUPERVISIONS,
    REQUIRED_AUTONOMOUS_SCHEMA_PROPERTIES,
    run_all_pf001a_validations,
    validate_autonomous_contract_doc,
    validate_composer_feasibility_audit,
    validate_pf001a_autonomous_schema,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "data/reviews/pf001/pf001_construct_registry.json"
HUMAN_SCHEMA_PATH = REPO_ROOT / "data/schemas/pf001_listener_observation.schema.json"
AUTONOMOUS_SCHEMA_PATH = (
    REPO_ROOT / "data/schemas/pf001_autonomous_listener_observation.schema.json"
)
POLICY_PATH = REPO_ROOT / "docs/research/PF001_GENERALIZATION_AND_SPLIT_POLICY.md"
FEASIBILITY_JSON_PATH = REPO_ROOT / "data/reviews/pf001/pf001_composer_corpus_feasibility.json"
FEASIBILITY_MD_PATH = REPO_ROOT / "docs/research/PF001_COMPOSER_CORPUS_FEASIBILITY_AUDIT.md"
AUTONOMOUS_CONTRACT_PATH = REPO_ROOT / "docs/research/PF001A_AUTONOMOUS_LISTENER_CONTRACT.md"
RC012_RESULT_PATH = REPO_ROOT / "data/reviews/rc012/rc012_one_shot_confirmatory_result.json"


def test_construct_registry_ids_and_completeness() -> None:
    assert REGISTRY_PATH.exists(), f"Registry file missing: {REGISTRY_PATH}"
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    constructs = data.get("constructs", [])
    assert len(constructs) >= 22, f"Expected >= 22 constructs, found {len(constructs)}"

    seen_ids: set[str] = set()
    for c in constructs:
        cid = c.get("construct_id")
        assert cid, f"Missing construct_id in construct: {c}"
        assert cid not in seen_ids, f"Duplicate construct_id: {cid}"
        seen_ids.add(cid)

        for field in REQUIRED_CONSTRUCT_FIELDS:
            assert field in c, f"Construct '{cid}' missing required field: '{field}'"

        status = c.get("current_status")
        assert status in ALLOWED_STATUSES, f"Construct '{cid}' invalid status: {status}"
        assert c.get("learning_supervision") in ALLOWED_LEARNING_SUPERVISIONS
        assert c.get("claim_scope") in ALLOWED_CLAIM_SCOPES


def test_human_participant_data_not_required_for_stage0() -> None:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    stage0_constructs = [c for c in data["constructs"] if c.get("stage_0_scope") is True]
    assert len(stage0_constructs) >= 5, "Expected at least 5 stage-0 constructs"

    for c in stage0_constructs:
        cid = c["construct_id"]
        # Stage-0 constructs must be purely structural
        assert c["claim_scope"] == "STRUCTURAL", (
            f"Stage-0 construct '{cid}' has claim_scope '{c['claim_scope']}', must be 'STRUCTURAL'"
        )
        assert c["learning_supervision"] != "HUMAN_VALIDATION_REQUIRED_FOR_SUBJECTIVE_CLAIM", (
            f"Stage-0 construct '{cid}' improperly requires human validation"
        )


def test_structural_and_subjective_claims_not_conflated() -> None:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for c in data["constructs"]:
        cid = c["construct_id"]
        if c["claim_scope"] == "SUBJECTIVE_HUMAN":
            assert c["learning_supervision"] == "HUMAN_VALIDATION_REQUIRED_FOR_SUBJECTIVE_CLAIM", (
                f"Subjective human construct '{cid}' lacks required human validation gating"
            )
            assert not c.get("stage_0_scope", False), (
                f"Subjective human construct '{cid}' cannot be in autonomous Stage-0"
            )


def test_no_high_level_not_operational_used_as_optimization_score() -> None:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    banned_concepts = [
        c
        for c in data["constructs"]
        if c.get("current_status") in {"HIGH_LEVEL_NOT_OPERATIONAL", "REJECTED_AS_DIRECT_SCALAR"}
    ]
    assert len(banned_concepts) >= 4, (
        "Expected at least 4 banned / non-operational high-level concepts"
    )

    for c in banned_concepts:
        cid = c["construct_id"]
        assert c.get("model_output") is None, (
            f"Construct '{cid}' ({c['current_status']}) must have model_output=None"
        )
        assert c.get("stage_0_scope") is not True, (
            f"Construct '{cid}' ({c['current_status']}) cannot be in Stage-0 scope"
        )


def test_stage_0_scope_contains_exactly_approved_constructs() -> None:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    stage0_constructs = [c for c in data["constructs"] if c.get("stage_0_scope") is True]
    found_namespaces = {c.get("stage_0_namespace") for c in stage0_constructs}

    assert found_namespaces == STAGE_0_APPROVED_NAMESPACES, (
        f"Stage-0 namespaces mismatch. Expected {STAGE_0_APPROVED_NAMESPACES}, found {found_namespaces}"
    )


def test_provisional_composer_cohorts_cannot_be_frozen_without_feasibility_pass() -> None:
    ok, errors = validate_composer_feasibility_audit(FEASIBILITY_JSON_PATH, FEASIBILITY_MD_PATH)
    assert ok, f"Feasibility audit failed: {errors}"

    with open(FEASIBILITY_JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    assert data["status"] == "PROVISIONAL_PENDING_CORPUS_FEASIBILITY_AUDIT"
    assert data["audit_findings"]["external_test_held_out_ready"] is False
    assert "Taneyev" in json.dumps(data["composer_cohorts"]["external_test_held_out"])


def test_autonomous_observation_schema_properties_and_multi_scale() -> None:
    ok, errors = validate_pf001a_autonomous_schema(AUTONOMOUS_SCHEMA_PATH)
    assert ok, f"Autonomous schema validation failed: {errors}"

    with open(AUTONOMOUS_SCHEMA_PATH, encoding="utf-8") as f:
        schema = json.load(f)

    props = schema.get("properties", {})
    for req_prop in REQUIRED_AUTONOMOUS_SCHEMA_PROPERTIES:
        assert req_prop in props, f"Missing required property: {req_prop}"

    # Verify no human participant fields in autonomous schema
    assert "listener_id" not in props
    assert "human_response" not in props
    assert "human_confidence" not in props


def test_optional_human_schema_preservation() -> None:
    assert HUMAN_SCHEMA_PATH.exists(), f"Optional human schema missing: {HUMAN_SCHEMA_PATH}"
    with open(HUMAN_SCHEMA_PATH, encoding="utf-8") as f:
        schema = json.load(f)
    for req_prop in REQUIRED_SCHEMA_PROPERTIES:
        assert req_prop in schema.get("properties", {})


def test_autonomous_contract_doc_contains_gates_and_anti_copy() -> None:
    ok, errors = validate_autonomous_contract_doc(AUTONOMOUS_CONTRACT_PATH)
    assert ok, f"Autonomous contract doc validation failed: {errors}"


def test_rc012_artifacts_remain_strictly_unchanged() -> None:
    ok, errors = validate_rc012_immutability(REPO_ROOT)
    assert ok, f"RC-012 immutability audit failed: {errors}"

    assert RC012_RESULT_PATH.exists()
    with open(RC012_RESULT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    assert data["confirmatory_result_hash"] == RC012_EXPECTED_RESULT_CANONICAL_HASH
    assert data["repertoire_summary"]["total_pieces"] == 483
    assert data["repertoire_summary"]["piece_ledger_sha256"] == RC012_EXPECTED_PIECE_LEDGER_HASH
    assert (
        data["secondary_metrics"]["bootstrap_replicate_matrix_sha256"]
        == RC012_EXPECTED_BOOTSTRAP_MATRIX_HASH
    )


def test_both_validation_scripts_pass_cleanly() -> None:
    res1 = run_all_contract_validations(REPO_ROOT)
    assert res1["passed"] is True, f"PF-001 validator failed: {res1['errors']}"

    res2 = run_all_pf001a_validations(REPO_ROOT)
    assert res2["passed"] is True, f"PF-001A validator failed: {res2['errors']}"

"""PF-001 Measurement Contract Regression Test Suite.

Verifies the scientific contract invariants of PF-001:
1. All registered constructs have IDs and mandatory fields.
2. Every MEASURABLE_NOW construct has an empirical human observable.
3. Every model target has an independent human target.
4. No HIGH_LEVEL_NOT_OPERATIONAL / REJECTED_AS_DIRECT_SCALAR concept is an optimization objective.
5. Stage-0 contains exactly the approved initial constructs (expectation, uncertainty, closure, recognition, memory).
6. Measurement timescale is declared for all constructs.
7. Human and AI variables are namespaced separately in the schema.
8. External-test split policy exists and enforces composer isolation.
9. Authoritative RC-012 result artifacts remain strictly unchanged.
"""

from __future__ import annotations

import json
import re
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
    validate_split_policy,
    validate_synthetic_dummy_observation,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "data/reviews/pf001/pf001_construct_registry.json"
SCHEMA_PATH = REPO_ROOT / "data/schemas/pf001_listener_observation.schema.json"
POLICY_PATH = REPO_ROOT / "docs/research/PF001_GENERALIZATION_AND_SPLIT_POLICY.md"
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


def test_measurable_now_have_human_observables() -> None:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    measurable_constructs = [
        c for c in data["constructs"] if c.get("current_status") == "MEASURABLE_NOW"
    ]
    assert len(measurable_constructs) >= 5, "Expected at least 5 MEASURABLE_NOW constructs"

    for c in measurable_constructs:
        cid = c["construct_id"]
        h_obs = c.get("human_observable")
        assert h_obs is not None and isinstance(h_obs, str) and len(h_obs.strip()) > 0, (
            f"MEASURABLE_NOW construct '{cid}' has no human_observable defined"
        )


def test_model_targets_have_independent_human_targets() -> None:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for c in data["constructs"]:
        cid = c["construct_id"]
        model_out = c.get("model_output")
        if model_out is not None:
            h_obs = c.get("human_observable")
            assert h_obs is not None and len(h_obs.strip()) > 0, (
                f"Construct '{cid}' declares model_output '{model_out}' without independent human_observable"
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
    assert len(stage0_constructs) >= 5, "Expected at least 5 stage-0 constructs"

    found_namespaces = set()
    for c in stage0_constructs:
        ns = c.get("stage_0_namespace")
        assert ns, f"Stage-0 construct '{c['construct_id']}' missing stage_0_namespace"
        base_ns = ns.split(".")[0]
        found_namespaces.add(base_ns)

    assert found_namespaces == STAGE_0_APPROVED_NAMESPACES, (
        f"Stage-0 namespaces mismatch. Expected {STAGE_0_APPROVED_NAMESPACES}, found {found_namespaces}"
    )


def test_measurement_timescale_declared() -> None:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for c in data["constructs"]:
        cid = c["construct_id"]
        ts = c.get("timescale")
        assert ts and isinstance(ts, str) and len(ts.strip()) > 0, (
            f"Construct '{cid}' lacks declared measurement timescale"
        )


def test_human_and_ai_variables_namespaced_separately() -> None:
    assert SCHEMA_PATH.exists(), f"Schema missing: {SCHEMA_PATH}"
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        schema = json.load(f)

    props = schema.get("properties", {})
    for req_prop in REQUIRED_SCHEMA_PROPERTIES:
        assert req_prop in props, f"Schema missing required property: '{req_prop}'"

    # Verify namespace separation
    model_props = [p for p in props if p.startswith("model_")]
    human_props = [
        p
        for p in props
        if p.startswith("human_")
        or p.startswith("recognition_")
        or p.startswith("recall_")
        or p == "response_time"
    ]

    assert len(model_props) >= 5, f"Expected >= 5 model properties, found {len(model_props)}"
    assert len(human_props) >= 10, f"Expected >= 10 human properties, found {len(human_props)}"

    # Ensure zero overlap
    overlap = set(model_props).intersection(set(human_props))
    assert len(overlap) == 0, f"Detected namespace collision in schema properties: {overlap}"


def test_schema_validates_synthetic_observation_record() -> None:
    ok, errors = validate_synthetic_dummy_observation(SCHEMA_PATH)
    assert ok, f"Synthetic observation record failed schema validation: {errors}"

    # Verify listener_id strictly complies with pseudonymous format (no PII)
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        schema = json.load(f)
    pattern = schema["properties"]["listener_id"]["pattern"]
    assert re.match(pattern, "LST-9876FEDCBA")
    assert not re.match(pattern, "JohnDoe@example.com")
    assert not re.match(pattern, "AliceSmith_Piano")


def test_external_test_split_policy_exists_and_is_isolated() -> None:
    ok, errors = validate_split_policy(POLICY_PATH)
    assert ok, f"Split policy validation failed: {errors}"

    content = POLICY_PATH.read_text(encoding="utf-8")
    assert "PREDICTIVE_VALIDITY" in content
    assert "TEMPORAL_VALIDITY" in content
    assert "INTERVENTION_VALIDITY" in content
    assert "GENERALIZATION_VALIDITY" in content
    assert "Taneyev" in content
    assert "Bortkiewicz" in content


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


def test_validation_script_passes_cleanly() -> None:
    results = run_all_contract_validations(REPO_ROOT)
    assert results["passed"] is True, f"Validation script returned failure: {results['errors']}"
    assert results["status"] == "PASS"
    assert results["verifications"]["construct_registry"] == "PASS"
    assert results["verifications"]["observation_schema"] == "PASS"
    assert results["verifications"]["split_policy"] == "PASS"
    assert results["verifications"]["rc012_immutability"] == "PASS"
    assert results["verifications"]["synthetic_metadata_compliance"] == "PASS"

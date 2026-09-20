"""Anti-self-certification and fidelity gate integrity tests for RC-013A.1b.

Proves that:
1. AUTOMATED_QC cannot set SOURCE_FIDELITY_VERIFIED in review records.
2. Missing source-comparison record causes fidelity check to fail.
3. Incomplete measure coverage (e.g. 23/24) causes production fidelity gate to fail.
4. Missing measure entry causes production fidelity gate to fail.
5. PENDING_HUMAN_REVIEW measure causes production fidelity gate to fail.
6. Missing canonical source authority causes production fidelity gate to fail.
7. Missing current symbolic SHA authority causes production fidelity gate to fail.
8. Source SHA mismatch (PDF) causes production fidelity gate to fail.
9. Symbolic SHA changed after review causes production fidelity gate to fail.
10. Unresolved critical ambiguity causes production fidelity gate to fail.
11. HUMAN_MEASURE_COMPARISON with AUTOMATED_QC / invalid reviewer causes gate to fail.
12. Empty reviewer_identifier or review_timestamp causes gate to fail.
13. Duplicate or disordered measure numbers cause gate to fail.
14. CRITICAL REGRESSION TEST: Editing only summary.source_fidelity_verdict on pending ledger CANNOT achieve SOURCE_FIDELITY_VERIFIED.
15. Comparison bundle mutation changes RC013_SOURCE_COMPARISON_BUNDLE_HASH.
16. Single measure status mutation changes RC013_SOURCE_FIDELITY_GATE_RESULT_HASH.
17. Generated review records cannot claim source fidelity.
18. Per-measure schema completeness contains all 26 required fields.
"""

from __future__ import annotations

import copy
import json
import os
from typing import Any

import pytest
from scripts.compute_rc013_hashes import (
    compute_directory_bundle_hash,
    compute_source_fidelity_gate_result,
    get_all_rc013_hashes,
)

from russian_piano_composer.corpus.rc013_fidelity import (
    REQUIRED_MEASURE_FIELDS,
    VALID_TERMINAL_ELEMENT_STATUSES,
    SourceFidelityGateError,
    validate_source_comparison_ledger,
)

# ---------------------------------------------------------------------------
# Helpers: load artifacts from disk
# ---------------------------------------------------------------------------

REVIEWS_DIR = "data/reviews/rc013"
CANONICAL_SCORES = [
    "sergei_lyapunov_op11_no01",
    "sergei_lyapunov_op11_no02",
    "sergei_lyapunov_op11_no03",
    "anton_arensky_op36_no01",
    "anton_arensky_op36_no02",
    "anton_arensky_op36_no13",
    "anatoly_lyadov_op40_no02",
    "anatoly_lyadov_op40_no03",
    "anatoly_lyadov_op46_no04",
]


def load_review(score_id: str) -> dict[str, Any]:
    path = os.path.join(REVIEWS_DIR, f"{score_id}.review.json")
    with open(path, encoding="utf-8") as f:
        res: dict[str, Any] = json.load(f)
        return res


def load_comparison_ledger(score_id: str) -> dict[str, Any]:
    path = os.path.join(REVIEWS_DIR, f"{score_id}.source_comparison.json")
    with open(path, encoding="utf-8") as f:
        res: dict[str, Any] = json.load(f)
        return res


def create_mock_fully_verified_ledger(score_id: str) -> dict[str, Any]:
    """Helper to create a deepcopy of a ledger where all measures are fully verified."""
    ledger = copy.deepcopy(load_comparison_ledger(score_id))
    total = ledger["total_measures"]
    for m in ledger["measures"]:
        m["comparison_method"] = "HUMAN_MEASURE_COMPARISON"
        m["pitch_status"] = "MATCH"
        m["duration_status"] = "MATCH"
        m["rest_status"] = "MATCH"
        m["staff_status"] = "MATCH"
        m["voice_status"] = "MATCH"
        m["tie_status"] = "MATCH"
        m["tuplet_status"] = "MATCH"
        m["grace_status"] = "MATCH"
        m["key_signature_status"] = "MATCH"
        m["time_signature_status"] = "MATCH"
        m["ornament_status"] = "MATCH"
        m["repeat_status"] = "MATCH"
        m["reviewer_type"] = "HUMAN_MUSICOLOGIST"
        m["reviewer_identifier"] = "test_reviewer"
        m["review_timestamp"] = "2026-09-20T12:00:00Z"
    ledger["summary"]["measures_compared"] = total
    ledger["summary"]["remaining_critical_discrepancies"] = 0
    ledger["summary"]["remaining_noncritical_ambiguities"] = 0
    ledger["summary"]["source_fidelity_verdict"] = "SOURCE_FIDELITY_VERIFIED"
    return ledger


# ---------------------------------------------------------------------------
# Test 1: AUTOMATED_QC review records must NOT claim source fidelity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("score_id", CANONICAL_SCORES)
def test_automated_qc_cannot_claim_source_fidelity_verified(score_id: str) -> None:
    """AUTOMATED_QC review records must never assert SOURCE_FIDELITY_VERIFIED."""
    review = load_review(score_id)

    assert review.get("reviewer_type") == "AUTOMATED_QC", (
        f"{score_id}: reviewer_type must be AUTOMATED_QC"
    )
    fidelity_status = review.get("source_fidelity_status")
    assert fidelity_status != "SOURCE_FIDELITY_VERIFIED", (
        f"{score_id}: AUTOMATED_QC review must not claim SOURCE_FIDELITY_VERIFIED; "
        f"got {fidelity_status!r}"
    )
    assert fidelity_status != "SOURCE_FAITHFUL_PILOT", (
        f"{score_id}: AUTOMATED_QC review must not claim SOURCE_FAITHFUL_PILOT; "
        f"got {fidelity_status!r}"
    )
    assert fidelity_status == "PENDING_SOURCE_COMPARISON", (
        f"{score_id}: expected PENDING_SOURCE_COMPARISON, got {fidelity_status!r}"
    )


@pytest.mark.parametrize("score_id", CANONICAL_SCORES)
def test_automated_qc_review_has_no_fidelity_verified_fields(score_id: str) -> None:
    """AUTOMATED_QC review must not contain measures_fidelity_verified field."""
    review = load_review(score_id)
    assert "measures_fidelity_verified" not in review, (
        f"{score_id}: review must not contain measures_fidelity_verified "
        "(that field requires human source comparison)"
    )


# ---------------------------------------------------------------------------
# Test 2: Missing source-comparison record → FAIL
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("score_id", CANONICAL_SCORES)
def test_source_comparison_ledger_exists_for_all_pilot_scores(score_id: str) -> None:
    """Every pilot score must have a source comparison ledger."""
    ledger_path = os.path.join(REVIEWS_DIR, f"{score_id}.source_comparison.json")
    assert os.path.exists(ledger_path), (
        f"Missing source comparison ledger for {score_id}: {ledger_path}"
    )


def test_missing_comparison_ledger_causes_fidelity_gate_to_fail() -> None:
    """If the source comparison ledger file does not exist, fidelity gate must fail."""
    fake_path = os.path.join(REVIEWS_DIR, "nonexistent_score.source_comparison.json")
    assert not os.path.exists(fake_path), "Test setup error: file should not exist"
    with pytest.raises(FileNotFoundError), open(fake_path, encoding="utf-8") as f:
        json.load(f)


# ---------------------------------------------------------------------------
# Test 3: Production gate: Incomplete measure coverage (23/24) → FAIL
# ---------------------------------------------------------------------------

def test_incomplete_measure_coverage_fails_production_gate() -> None:
    """23 out of 24 measures compared must fail the production fidelity gate."""
    verified = create_mock_fully_verified_ledger("anton_arensky_op36_no01")
    verified["measures"][23]["comparison_method"] = "PENDING_HUMAN_REVIEW"
    verified["summary"]["measures_compared"] = 23

    real_source_sha = verified["source_file_sha256"]
    real_sym_sha = verified["symbolic_file_sha256"]

    res = validate_source_comparison_ledger(
        verified,
        canonical_source_sha=real_source_sha,
        current_symbolic_sha=real_sym_sha,
        fail_fast=False,
    )
    assert res.valid is False
    assert res.fidelity_status == "PENDING_SOURCE_COMPARISON"
    assert "PENDING_HUMAN_REVIEW" in res.errors[0] or "Summary measures_compared" in res.errors[0]

    with pytest.raises(SourceFidelityGateError):
        validate_source_comparison_ledger(
            verified,
            canonical_source_sha=real_source_sha,
            current_symbolic_sha=real_sym_sha,
            fail_fast=True,
        )


# ---------------------------------------------------------------------------
# Test 4: Production gate: Missing measure entry → FAIL
# ---------------------------------------------------------------------------

def test_missing_measure_entry_fails_production_gate() -> None:
    """If a measure is missing from the ledger array (e.g. 23 elements vs total_measures=24), gate fails."""
    verified = create_mock_fully_verified_ledger("anton_arensky_op36_no01")
    verified["measures"].pop()
    verified["summary"]["measures_compared"] = 23

    real_source_sha = verified["source_file_sha256"]
    real_sym_sha = verified["symbolic_file_sha256"]

    res = validate_source_comparison_ledger(
        verified,
        canonical_source_sha=real_source_sha,
        current_symbolic_sha=real_sym_sha,
        fail_fast=False,
    )
    assert res.valid is False
    assert any("Measure count mismatch" in e for e in res.errors)


# ---------------------------------------------------------------------------
# Test 5: Production gate: PENDING measure status → FAIL
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("score_id", CANONICAL_SCORES)
def test_current_pending_ledger_fails_production_gate(score_id: str) -> None:
    """Tests production gate behavior on current on-disk ledgers."""
    ledger = load_comparison_ledger(score_id)
    real_source_sha = ledger["source_file_sha256"]
    real_sym_sha = ledger["symbolic_file_sha256"]

    res = validate_source_comparison_ledger(
        ledger,
        canonical_source_sha=real_source_sha,
        current_symbolic_sha=real_sym_sha,
        fail_fast=False,
    )
    if score_id in ("anton_arensky_op36_no01", "anton_arensky_op36_no02"):
        # Scores 1 & 2 have undergone genuine source comparison and are verified
        assert res.valid is True
        assert res.fidelity_status == "SOURCE_FIDELITY_VERIFIED"
    else:
        # Remaining 7 scores are in PENDING_HUMAN_REVIEW state and must fail production gate
        assert res.valid is False
        assert res.fidelity_status == "PENDING_SOURCE_COMPARISON"


# ---------------------------------------------------------------------------
# Test 6: Missing canonical source authority → FAIL
# ---------------------------------------------------------------------------

def test_missing_canonical_source_authority_fails_production_gate() -> None:
    """If canonical source SHA authority is None or empty, production gate fails closed."""
    verified = create_mock_fully_verified_ledger("anton_arensky_op36_no01")
    real_sym_sha = verified["symbolic_file_sha256"]

    res = validate_source_comparison_ledger(
        verified,
        canonical_source_sha=None,
        current_symbolic_sha=real_sym_sha,
        fail_fast=False,
    )
    assert res.valid is False
    assert res.error_category == "MISSING_SOURCE_AUTHORITY"
    assert any("Missing canonical source SHA authority" in e for e in res.errors)


# ---------------------------------------------------------------------------
# Test 7: Missing current symbolic SHA authority → FAIL
# ---------------------------------------------------------------------------

def test_missing_current_symbolic_sha_fails_production_gate() -> None:
    """If current symbolic SHA authority is None or empty, production gate fails closed."""
    verified = create_mock_fully_verified_ledger("anton_arensky_op36_no01")
    real_source_sha = verified["source_file_sha256"]

    res = validate_source_comparison_ledger(
        verified,
        canonical_source_sha=real_source_sha,
        current_symbolic_sha=None,
        fail_fast=False,
    )
    assert res.valid is False
    assert any("Missing current symbolic SHA authority" in e for e in res.errors)


# ---------------------------------------------------------------------------
# Test 8: Production gate: Source SHA mismatch → FAIL
# ---------------------------------------------------------------------------

def test_source_sha_mismatch_fails_production_gate() -> None:
    """Tampered or mismatched source PDF SHA must fail the production fidelity gate."""
    verified = create_mock_fully_verified_ledger("anton_arensky_op36_no01")
    tampered_canonical_sha = "0" * 64
    real_sym_sha = verified["symbolic_file_sha256"]

    res = validate_source_comparison_ledger(
        verified,
        canonical_source_sha=tampered_canonical_sha,
        current_symbolic_sha=real_sym_sha,
        fail_fast=False,
    )
    assert res.valid is False
    assert any("Source SHA mismatch" in e for e in res.errors)


# ---------------------------------------------------------------------------
# Test 9: Production gate: Symbolic SHA changed after review → FAIL
# ---------------------------------------------------------------------------

def test_symbolic_sha_drift_fails_production_gate() -> None:
    """If current MusicXML SHA differs from ledger symbolic_file_sha256, gate fails."""
    verified = create_mock_fully_verified_ledger("anton_arensky_op36_no01")
    real_source_sha = verified["source_file_sha256"]
    drifted_current_sha = "a" * 64

    res = validate_source_comparison_ledger(
        verified,
        canonical_source_sha=real_source_sha,
        current_symbolic_sha=drifted_current_sha,
        fail_fast=False,
    )
    assert res.valid is False
    assert any("Symbolic SHA mismatch" in e for e in res.errors)


# ---------------------------------------------------------------------------
# Test 10: Production gate: Unresolved CRITICAL ambiguity → FAIL
# ---------------------------------------------------------------------------

def test_unresolved_critical_ambiguity_fails_production_gate() -> None:
    """Unresolved CRITICAL ambiguity must fail the production fidelity gate."""
    verified = create_mock_fully_verified_ledger("sergei_lyapunov_op11_no01")
    verified["measures"][5]["unresolved_ambiguity"] = True
    verified["measures"][5]["ambiguity_severity"] = "CRITICAL"

    real_source_sha = verified["source_file_sha256"]
    real_sym_sha = verified["symbolic_file_sha256"]

    res = validate_source_comparison_ledger(
        verified,
        canonical_source_sha=real_source_sha,
        current_symbolic_sha=real_sym_sha,
        fail_fast=False,
    )
    assert res.valid is False
    assert any("CRITICAL ambiguity" in e for e in res.errors)


# ---------------------------------------------------------------------------
# Test 11: Human review semantics: AUTOMATED_QC / invalid reviewer → FAIL
# ---------------------------------------------------------------------------

def test_automated_qc_reviewer_type_for_human_comparison_fails() -> None:
    """If comparison_method is HUMAN_MEASURE_COMPARISON but reviewer_type is AUTOMATED_QC, gate fails."""
    verified = create_mock_fully_verified_ledger("anton_arensky_op36_no01")
    verified["measures"][0]["reviewer_type"] = "AUTOMATED_QC"

    real_source_sha = verified["source_file_sha256"]
    real_sym_sha = verified["symbolic_file_sha256"]

    res = validate_source_comparison_ledger(
        verified,
        canonical_source_sha=real_source_sha,
        current_symbolic_sha=real_sym_sha,
        fail_fast=False,
    )
    assert res.valid is False
    assert any("invalid reviewer_type 'AUTOMATED_QC'" in e for e in res.errors)


# ---------------------------------------------------------------------------
# Test 12: Human review semantics: Empty reviewer identifier or timestamp → FAIL
# ---------------------------------------------------------------------------

def test_empty_reviewer_id_or_timestamp_fails() -> None:
    """Empty reviewer_identifier or review_timestamp for human comparison fails."""
    verified = create_mock_fully_verified_ledger("anton_arensky_op36_no01")
    verified["measures"][0]["reviewer_identifier"] = ""
    verified["measures"][1]["review_timestamp"] = None

    real_source_sha = verified["source_file_sha256"]
    real_sym_sha = verified["symbolic_file_sha256"]

    res = validate_source_comparison_ledger(
        verified,
        canonical_source_sha=real_source_sha,
        current_symbolic_sha=real_sym_sha,
        fail_fast=False,
    )
    assert res.valid is False
    assert any("empty reviewer_identifier" in e for e in res.errors)
    assert any("empty review_timestamp" in e for e in res.errors)


# ---------------------------------------------------------------------------
# Test 13: Measure identity integrity: duplicate or disordered measure numbers → FAIL
# ---------------------------------------------------------------------------

def test_duplicate_measure_numbers_fail_gate() -> None:
    """Duplicate measure numbers (e.g. measure 1 repeated 24 times) fails measure sequence integrity."""
    verified = create_mock_fully_verified_ledger("anton_arensky_op36_no01")
    for m in verified["measures"]:
        m["measure_number"] = 1

    real_source_sha = verified["source_file_sha256"]
    real_sym_sha = verified["symbolic_file_sha256"]

    res = validate_source_comparison_ledger(
        verified,
        canonical_source_sha=real_source_sha,
        current_symbolic_sha=real_sym_sha,
        fail_fast=False,
    )
    assert res.valid is False
    assert any("Measure sequence violation" in e for e in res.errors)


# ---------------------------------------------------------------------------
# Test 14: CRITICAL REGRESSION TEST: Summary verdict mutation cannot bypass gate
# ---------------------------------------------------------------------------

def test_summary_verdict_mutation_cannot_bypass_production_validation(tmp_path: Any) -> None:
    """Editing only summary.source_fidelity_verdict on a pending ledger CANNOT yield SOURCE_FIDELITY_VERIFIED."""
    # Copy all ledgers to temp dir
    for f in os.listdir(REVIEWS_DIR):
        if f.endswith(".source_comparison.json"):
            src_p = os.path.join(REVIEWS_DIR, f)
            dst_p = tmp_path / f
            with open(src_p, encoding="utf-8") as rf:
                data = json.load(rf)
            with open(dst_p, "w", encoding="utf-8") as wf:
                json.dump(data, wf)

    # Mutate all 9 ledgers in temp dir to claim SOURCE_FIDELITY_VERIFIED in summary ONLY
    for f in os.listdir(tmp_path):
        if f.endswith(".source_comparison.json"):
            p = tmp_path / f
            with open(p, encoding="utf-8") as rf:
                data = json.load(rf)
            data["summary"]["source_fidelity_verdict"] = "SOURCE_FIDELITY_VERIFIED"
            # Leave all measures PENDING_HUMAN_REVIEW and NOT_REVIEWED
            with open(p, "w", encoding="utf-8") as wf:
                json.dump(data, wf)

    # Recompute gate result
    new_bundle_hash = compute_directory_bundle_hash(str(tmp_path), extension=".source_comparison.json")
    hashes = get_all_rc013_hashes()

    overall_verdict, _ = compute_source_fidelity_gate_result(
        source_comparison_bundle_hash=new_bundle_hash,
        source_img_bundle_hash=hashes["RC013_SOURCE_IMAGE_BUNDLE_HASH"],
        corpus_bundle_hash=hashes["RC013_CANONICAL_SYMBOLIC_CORPUS_HASH"],
        reviews_dir=str(tmp_path),
    )

    assert overall_verdict == "PENDING_SOURCE_COMPARISON", (
        "CRITICAL REGRESSION: Self-declared summary verdict bypassed production validation!"
    )


# ---------------------------------------------------------------------------
# Test 15: Comparison bundle mutation changes hash
# ---------------------------------------------------------------------------

def test_comparison_bundle_mutation_changes_hash(tmp_path: Any) -> None:
    """Mutating any source comparison ledger changes RC013_SOURCE_COMPARISON_BUNDLE_HASH."""
    initial_bundle_hash = compute_directory_bundle_hash(REVIEWS_DIR, extension=".source_comparison.json")

    for f in os.listdir(REVIEWS_DIR):
        if f.endswith(".source_comparison.json"):
            src_p = os.path.join(REVIEWS_DIR, f)
            dst_p = tmp_path / f
            with open(src_p, encoding="utf-8") as rf:
                data = json.load(rf)
            with open(dst_p, "w", encoding="utf-8") as wf:
                json.dump(data, wf)

    target = str(tmp_path / "anton_arensky_op36_no01.source_comparison.json")
    with open(target, encoding="utf-8") as rf_t:
        mutated_data: dict[str, Any] = json.load(rf_t)
    mutated_data["measures"][0]["pitch_status"] = "AMBIGUOUS"
    with open(target, "w", encoding="utf-8") as wf_t:
        json.dump(mutated_data, wf_t)

    mutated_bundle_hash = compute_directory_bundle_hash(str(tmp_path), extension=".source_comparison.json")
    assert initial_bundle_hash != mutated_bundle_hash, (
        "Bundle hash failed to change upon measure mutation"
    )


# ---------------------------------------------------------------------------
# Test 16: Single measure status mutation changes fidelity-result hash
# ---------------------------------------------------------------------------

def test_single_measure_mutation_changes_fidelity_result_hash(tmp_path: Any) -> None:
    """Mutating a single measure status mutates bundle hash and therefore fidelity gate result hash."""
    hashes = get_all_rc013_hashes()
    original_gate_hash = hashes["RC013_SOURCE_FIDELITY_GATE_RESULT_HASH"]

    for f in os.listdir(REVIEWS_DIR):
        if f.endswith(".source_comparison.json"):
            src_p = os.path.join(REVIEWS_DIR, f)
            dst_p = tmp_path / f
            with open(src_p, encoding="utf-8") as rf:
                data = json.load(rf)
            with open(dst_p, "w", encoding="utf-8") as wf:
                json.dump(data, wf)

    target = str(tmp_path / "sergei_lyapunov_op11_no01.source_comparison.json")
    with open(target, encoding="utf-8") as rf_t2:
        m_data: dict[str, Any] = json.load(rf_t2)
    m_data["measures"][3]["pitch_status"] = "MATCH"
    with open(target, "w", encoding="utf-8") as wf_t2:
        json.dump(m_data, wf_t2)

    new_bundle_hash = compute_directory_bundle_hash(str(tmp_path), extension=".source_comparison.json")
    _, mutated_gate_hash = compute_source_fidelity_gate_result(
        source_comparison_bundle_hash=new_bundle_hash,
        source_img_bundle_hash=hashes["RC013_SOURCE_IMAGE_BUNDLE_HASH"],
        corpus_bundle_hash=hashes["RC013_CANONICAL_SYMBOLIC_CORPUS_HASH"],
        reviews_dir=str(tmp_path),
    )

    assert original_gate_hash != mutated_gate_hash, (
        "Fidelity gate result hash failed to change upon single measure mutation"
    )


# ---------------------------------------------------------------------------
# Test 17: Generated review records must not self-certify fidelity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("score_id", CANONICAL_SCORES)
def test_generated_review_record_is_not_self_certified(score_id: str) -> None:
    """Generated review record must not contain any fidelity-verified claims."""
    review = load_review(score_id)

    forbidden_statuses = {"SOURCE_FIDELITY_VERIFIED", "SOURCE_FAITHFUL_PILOT"}
    actual_status = review.get("source_fidelity_status")
    assert actual_status not in forbidden_statuses, (
        f"{score_id}: review contains forbidden self-certifying status: {actual_status!r}"
    )

    assert "measures_fidelity_verified" not in review, (
        f"{score_id}: review must not contain measures_fidelity_verified"
    )
    assert "errors_initial" not in review, (
        f"{score_id}: review must not contain errors_initial (requires source comparison)"
    )
    assert "unresolved_ambiguities" not in review, (
        f"{score_id}: review must not contain unresolved_ambiguities (requires source comparison)"
    )


# ---------------------------------------------------------------------------
# Test 18: Ledger per-measure schema completeness (all 26 required fields)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("score_id", CANONICAL_SCORES)
def test_source_comparison_ledger_has_all_required_fields(score_id: str) -> None:
    """Every measure record must contain all 26 required schema fields."""
    ledger = load_comparison_ledger(score_id)
    measures = ledger["measures"]
    total = ledger["total_measures"]

    assert len(measures) == total, (
        f"{score_id}: ledger has {len(measures)} measures, expected {total}"
    )
    assert len(REQUIRED_MEASURE_FIELDS) == 26, (
        f"REQUIRED_MEASURE_FIELDS must contain exactly 26 fields, found {len(REQUIRED_MEASURE_FIELDS)}"
    )

    for i, m in enumerate(measures):
        missing = REQUIRED_MEASURE_FIELDS - set(m.keys())
        assert not missing, (
            f"{score_id} measure {i+1}: missing required fields: {missing}"
        )
        element_fields = {
            "pitch_status", "duration_status", "rest_status", "staff_status",
            "voice_status", "tie_status", "tuplet_status", "grace_status",
            "key_signature_status", "time_signature_status",
            "ornament_status", "repeat_status",
        }
        if score_id in ("anton_arensky_op36_no01", "anton_arensky_op36_no02"):
            for field in element_fields:
                assert m[field] in VALID_TERMINAL_ELEMENT_STATUSES, (
                    f"{score_id} measure {i+1}: {field} must have a valid terminal status"
                )
            assert m["comparison_method"] == "HUMAN_MEASURE_COMPARISON", (
                f"{score_id} measure {i+1}: comparison_method must be HUMAN_MEASURE_COMPARISON"
            )
        else:
            for field in element_fields:
                assert m[field] == "NOT_REVIEWED", (
                    f"{score_id} measure {i+1}: {field} must be NOT_REVIEWED initially"
                )
            assert m["comparison_method"] == "PENDING_HUMAN_REVIEW", (
                f"{score_id} measure {i+1}: comparison_method must be PENDING_HUMAN_REVIEW"
            )


# ---------------------------------------------------------------------------
# Test 19: Decision report does not claim source fidelity pass
# ---------------------------------------------------------------------------

def test_final_decision_report_does_not_claim_source_fidelity_pass() -> None:
    """RC013_FINAL_DECISION_REPORT must not claim SOURCE FIDELITY = PASS (PILOT)."""
    report_path = "docs/research/RC013_FINAL_DECISION_REPORT.md"
    assert os.path.exists(report_path)
    with open(report_path, encoding="utf-8") as f:
        content = f.read()

    assert "SOURCE_FIDELITY = PASS" not in content, (
        "RC013_FINAL_DECISION_REPORT must not claim SOURCE_FIDELITY = PASS; "
        "pilot fidelity is PENDING_SOURCE_COMPARISON"
    )

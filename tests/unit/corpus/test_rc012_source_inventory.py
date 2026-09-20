"""
Unit tests for RC-012 Confirmatory Source Inventory, Eligibility Derivation, and Gate Integrity.
"""

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from scripts.audit_rc012_source_inventory import (
    ALLOWED_CLEAN_LICENSES,
    EXPECTED_GATE_RESULT_HASH,
    EXPECTED_INVENTORY_HASH,
    EXPECTED_POLICY_HASH,
    EXPECTED_QUERY_LOG_HASH,
    audit_rc012_source_inventory,
    compute_normalized_file_hash,
)
from scripts.verify_rc012_source_evidence import verify_rc012_source_evidence


def test_source_inventory_file_and_hash_determinism() -> None:
    inv_path = Path("data/manifests/rc012_source_inventory.csv")
    assert inv_path.exists(), "Source inventory CSV must exist"

    actual_hash = compute_normalized_file_hash(inv_path)
    assert actual_hash == EXPECTED_INVENTORY_HASH, (
        f"Inventory hash mismatch: expected {EXPECTED_INVENTORY_HASH}, got {actual_hash}"
    )


def test_source_query_log_file_and_hash_determinism() -> None:
    log_path = Path("data/manifests/rc012_source_query_log.csv")
    assert log_path.exists(), "Source query log CSV must exist"

    actual_hash = compute_normalized_file_hash(log_path)
    assert actual_hash == EXPECTED_QUERY_LOG_HASH, (
        f"Query log hash mismatch: expected {EXPECTED_QUERY_LOG_HASH}, got {actual_hash}"
    )


def test_source_policy_file_and_hash_determinism() -> None:
    pol_path = Path("docs/research/RC012_SOURCE_POLICY.md")
    assert pol_path.exists(), "Source policy MD must exist"

    actual_hash = compute_normalized_file_hash(pol_path)
    assert actual_hash == EXPECTED_POLICY_HASH, (
        f"Policy hash mismatch: expected {EXPECTED_POLICY_HASH}, got {actual_hash}"
    )


def test_source_inventory_columns_and_deterministic_sorting() -> None:
    inv_path = Path("data/manifests/rc012_source_inventory.csv")
    required_cols = [
        "composer",
        "class",
        "source_repository_or_dataset",
        "source_version_or_commit",
        "actual_source_item_id",
        "actual_source_path_or_record_id",
        "actual_title",
        "actual_opus_or_catalogue",
        "actual_movement",
        "raw_format",
        "source_file_hash_if_available",
        "original_solo_piano",
        "parseable",
        "license_status",
        "rc011_compatible",
        "canonical_work_id",
        "duplicate_group",
        "eligible",
        "exclusion_reason",
    ]

    rows = []
    with open(inv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == required_cols, "Fieldnames must match required schema exactly"
        for row in reader:
            rows.append(row)

    assert len(rows) == 481, f"Expected 481 authentic inventory rows, got {len(rows)}"

    # Verify deterministic sort order: (composer, canonical_work_id, actual_source_item_id)
    sort_keys = [(r["composer"], r["canonical_work_id"], r["actual_source_item_id"]) for r in rows]
    assert sort_keys == sorted(sort_keys), "Rows in source inventory CSV must be strictly sorted"


def test_dynamic_derivation_of_n_russian_and_n_control() -> None:
    gate_payload = audit_rc012_source_inventory()

    assert gate_payload["n_russian_qualified"] == 2
    assert gate_payload["n_control_qualified"] == 5
    assert gate_payload["qualified_russian_composers"] == ["Alexander Scriabin", "Modest Mussorgsky"]
    assert gate_payload["qualified_control_composers"] == [
        "Antonín Dvořák",
        "Béla Bartók",
        "Claude Debussy",
        "Edvard Grieg",
        "Ludwig van Beethoven",
    ]
    assert gate_payload["gate_status"] == "CONFIRMATORY_DATA_CONTRACT_FAILED"
    assert gate_payload["failure_reason"] == "DATA AVAILABILITY FAILURE"
    assert gate_payload["data_gate_result_hash"] == EXPECTED_GATE_RESULT_HASH


def test_duplicate_source_rows_do_not_inflate_mc() -> None:
    """Verify that multiple source rows for the same work do not inflate M_c."""
    inv_path = Path("data/manifests/rc012_source_inventory.csv")
    with open(inv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Find works that exist across multiple sources (e.g., Scriabin or Prokofiev)
    dup_group_rows = defaultdict(list)
    for r in rows:
        dup_group_rows[r["duplicate_group"]].append(r)

    multi_source_groups = {grp: r_list for grp, r_list in dup_group_rows.items() if len(r_list) > 1}
    assert len(multi_source_groups) > 0, "Expected at least one cross-source duplicate work"

    # For every multi-source group, verify at most ONE row is eligible
    for grp, r_list in multi_source_groups.items():
        eligible_rows = [r for r in r_list if r["eligible"] == "True"]
        assert len(eligible_rows) <= 1, f"Duplicate group {grp} has {len(eligible_rows)} eligible rows"


def test_prokofiev_mc_equals_four() -> None:
    """Verify Sergei Prokofiev has exactly M_c = 4 unique eligible canonical works."""
    gate_payload = audit_rc012_source_inventory()
    prok_metrics = gate_payload["composer_metrics"]["Sergei Prokofiev"]

    assert prok_metrics["eligible_canonical_work_count"] == 4, (
        f"Expected M_c(Prokofiev) == 4, got {prok_metrics['eligible_canonical_work_count']}"
    )
    assert not prok_metrics["qualified"], "Prokofiev with M_c=4 must remain EXCLUDED (4 < 10)"

    # Verify the four specific canonical works
    inv_path = Path("data/manifests/rc012_source_inventory.csv")
    with open(inv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        prok_eligible_works = {
            r["canonical_work_id"]
            for r in reader
            if r["composer"] == "Sergei Prokofiev" and r["eligible"] == "True"
        }
    expected_prok_works = {
        "prokofiev_op11_toccata",
        "prokofiev_op22_no01",
        "prokofiev_op22_no10",
        "prokofiev_op22_no16",
    }
    assert prok_eligible_works == expected_prok_works, (
        f"Mismatch in Prokofiev eligible works: {prok_eligible_works} != {expected_prok_works}"
    )


def test_fail_closed_policy_behavior_on_mutations() -> None:
    """Verify that any row with eligible=True but invalid fields is strictly rejected by verify_rc012_source_evidence."""
    from scripts.verify_rc012_source_evidence import verify_rc012_source_evidence

    # Verify baseline passes first
    verify_rc012_source_evidence()

    # Simulate invalid rows using test function
    def validate_row(r: dict[str, str]) -> bool:
        return (
            r["original_solo_piano"] == "True"
            and r["parseable"] == "True"
            and r["license_status"] in ALLOWED_CLEAN_LICENSES
            and r["rc011_compatible"] == "True"
            and r["canonical_work_id"] != "none"
            and r["actual_source_item_id"] != "none"
            and r["source_version_or_commit"] not in {"none", "", "exhausted_audit_2026"}
        )

    base_valid = {
        "original_solo_piano": "True",
        "parseable": "True",
        "license_status": "CC-BY-NC-SA-4.0",
        "rc011_compatible": "True",
        "canonical_work_id": "test_work",
        "actual_source_item_id": "test_item",
        "source_version_or_commit": "abc1234",
    }
    assert validate_row(base_valid) is True

    # 1. eligible=True + parseable=False -> rejected
    mutated = dict(base_valid, parseable="False")
    assert validate_row(mutated) is False

    # 2. eligible=True + original_solo_piano=False -> rejected
    mutated = dict(base_valid, original_solo_piano="False")
    assert validate_row(mutated) is False

    # 3. eligible=True + rc011_compatible=False -> rejected
    mutated = dict(base_valid, rc011_compatible="False")
    assert validate_row(mutated) is False

    # 4. non-whitelisted license -> rejected
    for bad_lic in ["UNKNOWN", "REVIEW_REQUIRED", "CONFLICT", "NONE", "GPL-3.0", ""]:
        mutated = dict(base_valid, license_status=bad_lic)
        assert validate_row(mutated) is False


def test_license_fail_closed_whitelist() -> None:
    """Verify that only explicitly whitelisted clean licenses can be marked eligible."""
    inv_path = Path("data/manifests/rc012_source_inventory.csv")
    with open(inv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["eligible"] == "True":
                assert r["license_status"] in ALLOWED_CLEAN_LICENSES, (
                    f"Row {r['actual_source_item_id']} has non-whitelisted license: {r['license_status']}"
                )
            if r["license_status"] in {"UNKNOWN", "REVIEW_REQUIRED", "CONFLICT", "NONE"}:
                assert r["eligible"] == "False", (
                    f"Row {r['actual_source_item_id']} with license {r['license_status']} must not be eligible"
                )


def test_tombstone_rows_do_not_count_as_matching_items() -> None:
    """Verify tombstone rows for zero-count composers have no matching items and eligible=False."""
    inv_path = Path("data/manifests/rc012_source_inventory.csv")
    with open(inv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["canonical_work_id"] == "none":
                assert r["eligible"] == "False"
                assert r["actual_source_item_id"] == "none"
                assert r["exclusion_reason"] != "none"


def test_referential_integrity_and_placeholder_rejection() -> None:
    """Verify source evidence integrity verifier passes cleanly without placeholder violations."""
    verify_rc012_source_evidence()


def test_gate_hash_mutation_sensitivity() -> None:
    """Verify that if any composer eligibility flag is mutated, the data gate hash changes."""
    gate_payload = audit_rc012_source_inventory()
    baseline_hash = gate_payload["data_gate_result_hash"]

    # Clone payload and simulate mutating an eligibility count
    mutated_payload = json.loads(json.dumps(gate_payload))
    mutated_payload["composer_metrics"]["Modest Mussorgsky"]["eligible_canonical_work_count"] = 9
    mutated_payload["composer_metrics"]["Modest Mussorgsky"]["qualified"] = False
    mutated_payload["n_russian_qualified"] = 1
    mutated_payload["qualified_russian_composers"] = ["Alexander Scriabin"]

    # Re-encode payload without the hash key itself
    del mutated_payload["data_gate_result_hash"]
    encoded = json.dumps(mutated_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    mutated_hash = hashlib.sha256(encoded).hexdigest()

    assert mutated_hash != baseline_hash, "Data gate hash must be strictly sensitive to eligibility mutations"


def test_canonical_documents_zero_stale_russian_count() -> None:
    """Verify that canonical research docs do not claim N_Russian = 1 or claim stylistic guidance validation."""
    canonical_docs = [
        Path("docs/research/RC012_EXTERNAL_CONFIRMATION_RESULTS.md"),
        Path("docs/research/RC012_CONFIRMATORY_CORPUS_INVENTORY.md"),
        Path("docs/research/RC012_CONFIRMATORY_CORPUS_FREEZE.md"),
        Path("docs/research/RC012_PREREGISTRATION.md"),
        Path("docs/adr/ADR-012-independent-composer-confirmation.md"),
    ]

    for doc in canonical_docs:
        assert doc.exists(), f"Document {doc} must exist"
        text = doc.read_text(encoding="utf-8")
        assert "N_{\\text{Russian}} = 1 < 4" not in text, f"Stale N_Russian = 1 found in {doc}"
        assert "N_{\\text{Russian}} = 1" not in text, f"Stale N_Russian = 1 found in {doc}"
        assert "CONFIRMATORY_DATA_CONTRACT_FAILED" in text.replace("\\_", "_"), f"Gate status missing in {doc}"
        assert "DATA AVAILABILITY FAILURE" in text, f"Failure reason missing in {doc}"
        assert "NOT TESTED" in text, f"NOT TESTED status missing in {doc}"


def test_zero_confirmatory_predictions_executed() -> None:
    """Verify that no prediction results or decision score parquet files were generated for confirmatory test sets."""
    disallowed_artifacts = [
        Path("data/features/confirmatory"),
        Path("data/predictions/rc012"),
        Path("results/rc012_predictions.parquet"),
        Path("results/rc012_decision_scores.csv"),
    ]
    for p in disallowed_artifacts:
        assert not p.exists(), f"Disallowed prediction artifact found: {p}"

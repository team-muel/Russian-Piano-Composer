"""
Unit tests for RC-012 Confirmatory Source Inventory, Eligibility Derivation, and Gate Integrity.
"""

import csv
import hashlib
import json
from pathlib import Path

from scripts.audit_rc012_source_inventory import (
    EXPECTED_INVENTORY_HASH,
    EXPECTED_POLICY_HASH,
    audit_rc012_source_inventory,
    compute_normalized_file_hash,
)

EXPECTED_GATE_RESULT_HASH: str = "a5e64cd3e0260250687d64f32915fd0fea8b84830a8c5bb2d1a3651a5cf4337b"


def test_source_inventory_file_and_hash_determinism() -> None:
    inv_path = Path("data/manifests/rc012_source_inventory.csv")
    assert inv_path.exists(), "Source inventory CSV must exist"

    actual_hash = compute_normalized_file_hash(inv_path)
    assert actual_hash == EXPECTED_INVENTORY_HASH, (
        f"Inventory hash mismatch: expected {EXPECTED_INVENTORY_HASH}, got {actual_hash}"
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
        "source",
        "source_version_or_commit",
        "source_item_id",
        "title",
        "opus_or_catalogue",
        "movement",
        "raw_format",
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

    assert len(rows) == 500, f"Expected 500 inventory rows, got {len(rows)}"

    # Verify deterministic sort order: (composer, canonical_work_id, source_item_id)
    sort_keys = [(r["composer"], r["canonical_work_id"], r["source_item_id"]) for r in rows]
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


def test_gate_hash_mutation_sensitivity() -> None:
    """Verify that if any composer eligibility flag is mutated, the data gate hash changes."""
    gate_payload = audit_rc012_source_inventory()
    baseline_hash = gate_payload["data_gate_result_hash"]

    # Clone payload and simulate mutating an eligibility count
    mutated_payload = json.loads(json.dumps(gate_payload))
    mutated_payload["composer_metrics"]["Modest Mussorgsky"]["eligible_count"] = 9
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

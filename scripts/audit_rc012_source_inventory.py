"""
Audit script for RC-012 Confirmatory Source Inventory and Data Contract Gate.

Parses data/manifests/rc012_source_inventory.csv, verifies policy adherence,
derives composer-level metrics dynamically, and computes cryptographic hashes:
1. RC012_SOURCE_INVENTORY_HASH
2. RC012_SOURCE_POLICY_HASH
3. RC012_DATA_GATE_RESULT_HASH

Enforces:
- Fail-closed gate evaluation (N_Russian >= 4 and N_Control >= 4).
- Reports exact status: CONFIRMATORY_DATA_CONTRACT_FAILED (DATA AVAILABILITY FAILURE).
- Zero prediction / zero feature extraction execution.
"""

import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

EXPECTED_POLICY_HASH: str = "f9f4fe75dad8eea1de7ae3acd5d80818d1ec24d16999a525bfb0eacc7ba718fc"
EXPECTED_INVENTORY_HASH: str = "40672c4fd54c3440e6c29db2e0c6f4aa5ffdb7dd7d88e020ff5eccaf015a9a12"



def compute_normalized_file_hash(path: Path) -> str:
    """Compute SHA256 of file bytes with newline canonicalization to LF."""
    raw = path.read_bytes()
    normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def audit_rc012_source_inventory() -> dict:
    print("--- Running RC-012 Confirmatory Source Inventory Audit ---")

    inventory_path = Path("data/manifests/rc012_source_inventory.csv")
    if not inventory_path.exists():
        raise FileNotFoundError(f"Source inventory not found: {inventory_path}")

    policy_path = Path("docs/research/RC012_SOURCE_POLICY.md")
    if not policy_path.exists():
        raise FileNotFoundError(f"Source policy not found: {policy_path}")

    # 1. Compute and verify inventory hash
    actual_inventory_hash = compute_normalized_file_hash(inventory_path)
    print(f"  RC012_SOURCE_INVENTORY_HASH: {actual_inventory_hash}")
    if actual_inventory_hash != EXPECTED_INVENTORY_HASH:
        raise ValueError(
            f"Inventory hash mismatch! Expected {EXPECTED_INVENTORY_HASH}, got {actual_inventory_hash}"
        )

    # 2. Compute and verify policy hash
    actual_policy_hash = compute_normalized_file_hash(policy_path)
    print(f"  RC012_SOURCE_POLICY_HASH:    {actual_policy_hash}")
    if actual_policy_hash != EXPECTED_POLICY_HASH:
        raise ValueError(
            f"Policy hash mismatch! Expected {EXPECTED_POLICY_HASH}, got {actual_policy_hash}"
        )

    # 3. Parse inventory and derive metrics
    rows: list[dict[str, str]] = []
    with open(inventory_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"  Total Inventory Rows Audited: {len(rows)}")

    # Group by composer
    composer_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        composer_rows[r["composer"]].append(r)

    composer_metrics: dict[str, dict] = {}
    qualified_russian: list[str] = []
    qualified_control: list[str] = []

    for composer, comp_rows in sorted(composer_rows.items()):
        comp_class = comp_rows[0]["class"]
        raw_count = len(comp_rows)
        # Deduplicate by canonical_work_id (excluding 'none' for tombstone rows)
        work_ids = {r["canonical_work_id"] for r in comp_rows if r["canonical_work_id"] != "none"}
        unique_work_count = len(work_ids) if work_ids else 0

        solo_count = sum(1 for r in comp_rows if r["original_solo_piano"] == "True")
        parseable_count = sum(1 for r in comp_rows if r["parseable"] == "True")
        license_count = sum(1 for r in comp_rows if r["license_status"] != "none")
        compatible_count = sum(1 for r in comp_rows if r["rc011_compatible"] == "True")
        eligible_count = sum(1 for r in comp_rows if r["eligible"] == "True")

        is_qualified = eligible_count >= 10
        if is_qualified:
            if comp_class == "Russian":
                qualified_russian.append(composer)
            elif comp_class == "Control":
                qualified_control.append(composer)

        composer_metrics[composer] = {
            "class": comp_class,
            "raw_count": raw_count,
            "unique_work_count": unique_work_count,
            "solo_piano_count": solo_count,
            "parseable_count": parseable_count,
            "license_clean_count": license_count,
            "rc011_compatible_count": compatible_count,
            "eligible_count": eligible_count,
            "qualified": is_qualified,
        }

    n_russian = len(qualified_russian)
    n_control = len(qualified_control)

    print(f"\n  Derived Qualified Russian Composers (M >= 10): {n_russian} ({qualified_russian})")
    print(f"  Derived Qualified Control Composers (M >= 10): {n_control} ({qualified_control})")

    # 4. Evaluate Data Contract Gate
    contract_passed = (n_russian >= 4) and (n_control >= 4)
    gate_status = "CONFIRMATORY_DATA_CONTRACT_PASSED" if contract_passed else "CONFIRMATORY_DATA_CONTRACT_FAILED"
    failure_reason = "NONE" if contract_passed else "DATA AVAILABILITY FAILURE"

    # Compute deterministic gate result payload & hash
    gate_result_payload = {
        "gate_status": gate_status,
        "failure_reason": failure_reason,
        "n_russian_qualified": n_russian,
        "n_control_qualified": n_control,
        "qualified_russian_composers": sorted(qualified_russian),
        "qualified_control_composers": sorted(qualified_control),
        "source_inventory_hash": actual_inventory_hash,
        "source_policy_hash": actual_policy_hash,
        "composer_metrics": composer_metrics,
    }

    gate_payload_encoded = json.dumps(gate_result_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    gate_result_hash = hashlib.sha256(gate_payload_encoded).hexdigest()

    print("\n==========================================================================")
    print(f" RC-012 DATA AVAILABILITY STATUS = {gate_status}")
    print(f" FAILURE REASON                  = {failure_reason}")
    print(f" RC012_DATA_GATE_RESULT_HASH    = {gate_result_hash}")
    print(" PRIMARY HYPOTHESIS STATUS       = NOT TESTED")
    print("==========================================================================")

    gate_result_payload["data_gate_result_hash"] = gate_result_hash
    return gate_result_payload


if __name__ == "__main__":
    try:
        audit_rc012_source_inventory()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

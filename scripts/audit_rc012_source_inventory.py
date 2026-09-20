"""
Audit script for RC-012 Confirmatory Source Inventory and Data Contract Gate.

Parses data/manifests/rc012_source_inventory.csv, verifies policy adherence,
derives composer-level metrics dynamically from deduplicated canonical work IDs,
and computes cryptographic hashes:
1. RC012_SOURCE_INVENTORY_HASH
2. RC012_SOURCE_QUERY_LOG_HASH
3. RC012_SOURCE_POLICY_HASH
4. RC012_DATA_GATE_RESULT_HASH

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

EXPECTED_INVENTORY_HASH: str = "4813102a193c38fc61ef4815a25895243c819b2527803f82e7020ac766627eb7"
EXPECTED_QUERY_LOG_HASH: str = "7bfbcd4af8c0651d4b5b65190be4c65ff86645655b4ebdcfa0b343d08388f5de"
EXPECTED_POLICY_HASH: str = "9ba534513398f398951de40110495e0725ae8ec7765ed0a8815d428df4bac497"
EXPECTED_GATE_RESULT_HASH: str = "85398969b0abbc2873544cc4b4dbdffbe1d4db6d665fa99aa4de237e4222d4ab"

ALLOWED_CLEAN_LICENSES: set[str] = {
    "CC0-1.0",
    "CC-BY-4.0",
    "CC-BY-SA-4.0",
    "CC-BY-NC-4.0",
    "CC-BY-NC-SA-4.0",
    "PUBLIC_DOMAIN",
    "ACADEMIC_RESEARCH_ONLY",
}


def compute_normalized_file_hash(path: Path) -> str:
    """Compute SHA256 of file bytes with newline canonicalization to LF."""
    raw = path.read_bytes()
    normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def audit_rc012_source_inventory() -> dict[str, object]:
    print("--- Running RC-012 Confirmatory Source Inventory Audit ---")

    inventory_path = Path("data/manifests/rc012_source_inventory.csv")
    if not inventory_path.exists():
        raise FileNotFoundError(f"Source inventory not found: {inventory_path}")

    query_log_path = Path("data/manifests/rc012_source_query_log.csv")
    if not query_log_path.exists():
        raise FileNotFoundError(f"Source query log not found: {query_log_path}")

    policy_path = Path("docs/research/RC012_SOURCE_POLICY.md")
    if not policy_path.exists():
        raise FileNotFoundError(f"Source policy not found: {policy_path}")

    # 1. Verify inventory hash
    actual_inventory_hash = compute_normalized_file_hash(inventory_path)
    print(f"  RC012_SOURCE_INVENTORY_HASH: {actual_inventory_hash}")
    if actual_inventory_hash != EXPECTED_INVENTORY_HASH:
        raise ValueError(
            f"Inventory hash mismatch! Expected {EXPECTED_INVENTORY_HASH}, got {actual_inventory_hash}"
        )

    # 2. Verify query log hash
    actual_query_log_hash = compute_normalized_file_hash(query_log_path)
    print(f"  RC012_SOURCE_QUERY_LOG_HASH: {actual_query_log_hash}")
    if actual_query_log_hash != EXPECTED_QUERY_LOG_HASH:
        raise ValueError(
            f"Query log hash mismatch! Expected {EXPECTED_QUERY_LOG_HASH}, got {actual_query_log_hash}"
        )

    # 3. Verify policy hash
    actual_policy_hash = compute_normalized_file_hash(policy_path)
    print(f"  RC012_SOURCE_POLICY_HASH:    {actual_policy_hash}")
    if actual_policy_hash != EXPECTED_POLICY_HASH:
        raise ValueError(
            f"Policy hash mismatch! Expected {EXPECTED_POLICY_HASH}, got {actual_policy_hash}"
        )

    # 4. Parse inventory and derive metrics
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

    composer_metrics: dict[str, dict[str, object]] = {}
    qualified_russian: list[str] = []
    qualified_control: list[str] = []

    for composer, comp_rows in sorted(composer_rows.items()):
        comp_class = comp_rows[0]["class"]
        source_evidence_row_count = len(comp_rows)
        raw_matching_item_count = sum(1 for r in comp_rows if r["actual_source_item_id"] != "none")
        work_ids = {r["canonical_work_id"] for r in comp_rows if r["canonical_work_id"] != "none"}
        unique_canonical_work_count = len(work_ids)

        solo_count = sum(1 for r in comp_rows if r["original_solo_piano"] == "True")
        parseable_count = sum(1 for r in comp_rows if r["parseable"] == "True")
        license_count = sum(1 for r in comp_rows if r["license_status"] in ALLOWED_CLEAN_LICENSES)
        compatible_count = sum(1 for r in comp_rows if r["rc011_compatible"] == "True")

        # Deduplicated eligible canonical work IDs drive composer qualification M_c
        eligible_canonical_work_ids = {
            r["canonical_work_id"]
            for r in comp_rows
            if r["eligible"] == "True"
            and r["canonical_work_id"] != "none"
            and r["license_status"] in ALLOWED_CLEAN_LICENSES
        }
        m_c = len(eligible_canonical_work_ids)

        is_qualified = m_c >= 10
        if is_qualified:
            if comp_class == "Russian":
                qualified_russian.append(composer)
            elif comp_class == "Control":
                qualified_control.append(composer)

        composer_metrics[composer] = {
            "class": comp_class,
            "source_evidence_row_count": source_evidence_row_count,
            "raw_matching_item_count": raw_matching_item_count,
            "unique_canonical_work_count": unique_canonical_work_count,
            "solo_piano_count": solo_count,
            "parseable_count": parseable_count,
            "license_clean_count": license_count,
            "rc011_compatible_count": compatible_count,
            "eligible_canonical_work_count": m_c,
            "qualified": is_qualified,
        }

    n_russian = len(qualified_russian)
    n_control = len(qualified_control)

    print(f"\n  Derived Qualified Russian Composers (M_c >= 10): {n_russian} ({qualified_russian})")
    print(f"  Derived Qualified Control Composers (M_c >= 10): {n_control} ({qualified_control})")

    # 5. Evaluate Data Contract Gate
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
        "source_query_log_hash": actual_query_log_hash,
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

    if gate_result_hash != EXPECTED_GATE_RESULT_HASH:
        raise ValueError(
            f"Data gate result hash mismatch! Expected {EXPECTED_GATE_RESULT_HASH}, got {gate_result_hash}"
        )

    gate_result_payload["data_gate_result_hash"] = gate_result_hash
    return gate_result_payload


if __name__ == "__main__":
    try:
        audit_rc012_source_inventory()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

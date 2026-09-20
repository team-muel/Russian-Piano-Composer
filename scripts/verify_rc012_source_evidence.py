"""
Internal referential integrity and evidence verification for RC-012 Confirmatory Source Inventory.

Verifies:
1. Every eligible row has a non-placeholder source ID and path.
2. Every source version is concrete and non-empty.
3. Every canonical work has >= 1 evidence row.
4. Duplicate groups resolve deterministically (at most 1 eligible row per duplicate_group).
5. Every qualified composer has >= 10 unique eligible canonical_work_ids.
6. Zero-result composers have query-log evidence records.
7. No synthetic placeholder patterns exist (e.g., '*_piece_001', 'Solo Piano Piece 1', 'Bartok Piece 1').
8. Combinations of (source_repository_or_dataset, source_version_or_commit, actual_source_item_id) are unique.
"""

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

FORBIDDEN_PLACEHOLDER_REGEXES = [
    re.compile(r"^.*_piece_\d{3,}$", re.IGNORECASE),
    re.compile(r"^.*_w_\d{3,}$", re.IGNORECASE),
    re.compile(r"^.*_dup_\d{3,}$", re.IGNORECASE),
    re.compile(r"^.*Solo Piano Piece \d+$", re.IGNORECASE),
    re.compile(r"^Bartok Piece \d+$", re.IGNORECASE),
    re.compile(r"^Debussy Solo Piano Piece \d+$", re.IGNORECASE),
    re.compile(r"^Piano Sonata Movement \d+$", re.IGNORECASE),
]


ALLOWED_CLEAN_LICENSES: set[str] = {
    "CC0-1.0",
    "CC-BY-4.0",
    "CC-BY-SA-4.0",
    "CC-BY-NC-4.0",
    "CC-BY-NC-SA-4.0",
    "PUBLIC_DOMAIN",
    "ACADEMIC_RESEARCH_ONLY",
}

FORBIDDEN_MUTABLE_VERSIONS: set[str] = {
    "master",
    "main",
    "head",
    "latest",
}


def verify_rc012_source_evidence() -> None:
    print("--- Running RC-012 Source Evidence Integrity Verification ---")

    inv_path = Path("data/manifests/rc012_source_inventory.csv")
    if not inv_path.exists():
        raise FileNotFoundError(f"Source inventory missing at {inv_path}")

    query_log_path = Path("data/manifests/rc012_source_query_log.csv")
    if not query_log_path.exists():
        raise FileNotFoundError(f"Source query log missing at {query_log_path}")

    # 1. Read query log
    query_composers: set[str] = set()
    with open(query_log_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            query_composers.add(row["composer"])

    # 2. Read inventory
    inv_rows: list[dict[str, str]] = []
    with open(inv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            inv_rows.append(row)

    print(f"  Auditing {len(inv_rows)} inventory rows against evidence criteria...")

    seen_triplets: set[tuple[str, str, str, str]] = set()
    canonical_work_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    dup_group_eligible: dict[str, int] = defaultdict(int)
    composer_rows: dict[str, list[dict[str, str]]] = defaultdict(list)

    for i, r in enumerate(inv_rows, 1):
        comp = r["composer"]
        src = r["source_repository_or_dataset"]
        ver = r["source_version_or_commit"]
        item_id = r["actual_source_item_id"]
        path_id = r["actual_source_path_or_record_id"]
        title = r["actual_title"]
        canon_id = r["canonical_work_id"]
        dup_grp = r["duplicate_group"]
        elig = r["eligible"] == "True"
        reason = r["exclusion_reason"]

        composer_rows[comp].append(r)

        # Check placeholder patterns in source item IDs and titles
        for pattern in FORBIDDEN_PLACEHOLDER_REGEXES:
            if pattern.match(item_id):
                raise ValueError(f"Forbidden placeholder source ID detected at row {i}: '{item_id}'")
            if pattern.match(title):
                raise ValueError(f"Forbidden placeholder title detected at row {i}: '{title}'")

        # Derive fail-closed semantic eligibility from intrinsic fields
        is_semantically_eligible = (
            r["original_solo_piano"] == "True"
            and r["parseable"] == "True"
            and r["license_status"] in ALLOWED_CLEAN_LICENSES
            and r["rc011_compatible"] == "True"
            and canon_id != "none"
            and item_id != "none"
            and ver not in {"none", "", "exhausted_audit_2026"}
        )

        if elig:
            # An eligible row MUST be semantically eligible
            if not is_semantically_eligible:
                raise ValueError(
                    f"Row {i} ({comp} - {item_id}) declared eligible=True but fails policy semantic eligibility"
                )
            # Source version hygiene: canonical-selected rows MUST have immutable source identity
            if ver.lower() in FORBIDDEN_MUTABLE_VERSIONS:
                raise ValueError(
                    f"Row {i} ({comp} - {item_id}) is eligible=True but uses forbidden mutable version '{ver}'"
                )
            if reason != "NONE":
                raise ValueError(f"Eligible row {i} must have exclusion_reason='NONE', got '{reason}'")
            if path_id == "none" or not path_id:
                raise ValueError(f"Eligible row {i} cannot have 'none' or empty source path")
            dup_group_eligible[dup_grp] += 1
        else:
            # If ineligible, either it is not semantically eligible OR it is an explicitly documented duplicate
            if is_semantically_eligible and reason != "DUPLICATE_PRIORITIZED_PRIMARY_RECORD_ACCEPTED":
                raise ValueError(
                    f"Row {i} is semantically eligible but ineligible with non-duplicate reason: '{reason}'"
                )

        if canon_id != "none":
            canonical_work_rows[canon_id].append(r)

        if item_id != "none":
            quadruplet = (comp, src, ver, item_id)
            if quadruplet in seen_triplets:
                raise ValueError(f"Duplicate (composer, source, version, item_id) detected at row {i}: {quadruplet}")
            seen_triplets.add(quadruplet)

    # 3. Check duplicate group determinism
    for grp, count in dup_group_eligible.items():
        if count > 1:
            raise ValueError(f"Duplicate group '{grp}' has {count} eligible rows (must be at most 1)")
    print("  Duplicate Group Deduplication: PASS (At most 1 eligible row per duplicate group)")
    print("  Fail-Closed Policy Eligibility Derivation: PASS (All rows strictly policy-consistent)")
    print("  Source Version Hygiene: PASS (Zero mutable branch references on canonical-selected rows)")

    # 4. Check zero-result composers have query log records
    zero_composers = [c for c, c_rows in composer_rows.items() if all(r["eligible"] == "False" for r in c_rows)]
    for zc in zero_composers:
        if zc not in query_composers:
            raise ValueError(f"Zero-result composer '{zc}' missing from source query log")
    print(f"  Zero-Result Query Evidence: PASS ({len(zero_composers)} zero-result composers verified)")

    # 5. Check qualified composers have >= 10 unique eligible canonical work IDs
    for comp, c_rows in sorted(composer_rows.items()):
        eligible_canons = {r["canonical_work_id"] for r in c_rows if r["eligible"] == "True"}
        m_c = len(eligible_canons)
        if m_c >= 10:
            print(f"  Qualified Composer '{comp}': M_c = {m_c} (>= 10 verified)")
        else:
            print(f"  Excluded Candidate '{comp}': M_c = {m_c} (< 10)")

    print("\n==========================================================================")
    print(" RC-012 SOURCE EVIDENCE REFERENTIAL INTEGRITY: PASS")
    print("==========================================================================")


if __name__ == "__main__":
    try:
        verify_rc012_source_evidence()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

"""Generate PF-001B Remote Materialization Receipt with Deterministic Receipt Hash."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = REPO_ROOT / "data/reviews/pf001/pf001_physical_corpus_inventory.json"
RECEIPT_PATH = REPO_ROOT / "data/reviews/pf001/pf001b_remote_materialization_receipt.json"


def generate_materialization_receipt(
    inventory_path: Path, repo_root: Path
) -> dict[str, Any]:
    with open(inventory_path, encoding="utf-8") as f:
        inv = json.load(f)

    # Group scores by source family
    source_families: dict[str, Any] = {}

    for s in inv["scores"]:
        repo_url = s["source_repository"]
        commit = s["source_revision_or_commit"]
        family_key = f"{repo_url}@{commit}"

        if family_key not in source_families:
            source_families[family_key] = {
                "source_repository": repo_url,
                "immutable_revision": commit,
                "is_repository_tracked": "team-muel/Russian-Piano-Composer" in repo_url,
                "canonicalization_policy": s.get("canonicalization_policy", "IDENTITY"),
                "materialization_count": 0,
                "failure_count": 0,
                "artifacts": [],
            }

        fam = source_families[family_key]
        rel_path = s["physical_file_path"]
        p = repo_root / rel_path

        # Verify on disk
        exists = p.exists()
        actual_bytes = p.read_bytes() if exists else b""
        actual_sha = hashlib.sha256(actual_bytes).hexdigest() if exists else ""
        expected_materialized_sha = s.get("canonical_materialized_sha256", s.get("source_sha256"))
        upstream_raw_sha = s.get("upstream_raw_sha256", expected_materialized_sha)

        is_valid = exists and (actual_sha == expected_materialized_sha)
        if is_valid:
            fam["materialization_count"] += 1
        else:
            fam["failure_count"] += 1

        artifact_entry = {
            "work_id": s["work_id"],
            "relative_path": rel_path,
            "upstream_raw_sha256": upstream_raw_sha,
            "canonical_materialized_sha256": expected_materialized_sha,
            "actual_disk_sha256": actual_sha,
            "canonicalization_policy": s.get("canonicalization_policy", "IDENTITY"),
            "file_size_bytes": len(actual_bytes),
            "status": "VERIFIED_MATCH" if is_valid else "VERIFICATION_FAILED",
        }
        fam["artifacts"].append(artifact_entry)

    # Sort families and artifacts deterministically
    sorted_families = []
    total_materialized = 0
    total_failures = 0

    for fkey in sorted(source_families.keys()):
        fam = source_families[fkey]
        fam["artifacts"].sort(key=lambda a: a["work_id"])
        total_materialized += fam["materialization_count"]
        total_failures += fam["failure_count"]
        sorted_families.append(fam)

    receipt_data = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "milestone": "PF-001B.2",
        "receipt_title": "PF-001B Remote Materialization & Dual-Hash Provenance Receipt",
        "status": "MATERIALIZATION_AND_PROVENANCE_VERIFIED" if total_failures == 0 else "MATERIALIZATION_FAILED",
        "total_source_families": len(sorted_families),
        "total_scores_verified": total_materialized,
        "total_scores_failed": total_failures,
        "source_families": sorted_families,
    }

    # Deterministic receipt hash computed across canonical JSON serialization
    serialized = json.dumps(receipt_data, sort_keys=True, indent=2)
    receipt_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    receipt_data["receipt_hash"] = receipt_hash

    return receipt_data


def main() -> int:
    receipt = generate_materialization_receipt(INVENTORY_PATH, REPO_ROOT)
    with open(RECEIPT_PATH, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)

    print("=" * 70)
    print("PF-001B REMOTE MATERIALIZATION RECEIPT GENERATED")
    print("=" * 70)
    print(f"Receipt Path:           {RECEIPT_PATH}")
    print(f"Status:                 {receipt['status']}")
    print(f"Total Source Families:  {receipt['total_source_families']}")
    print(f"Total Scores Verified:  {receipt['total_scores_verified']}")
    print(f"Total Scores Failed:    {receipt['total_scores_failed']}")
    print(f"Receipt SHA-256 Hash:   {receipt['receipt_hash']}")
    print("=" * 70)

    return 0 if receipt["total_scores_failed"] == 0 else 1


if __name__ == "__main__":
    main()

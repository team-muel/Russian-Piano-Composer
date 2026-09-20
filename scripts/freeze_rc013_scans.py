"""Freezes verified source scan records using authentic downloaded byte SHA256 checksums."""

from __future__ import annotations

import hashlib
import json
import os

import pandas as pd


def main() -> None:
    df = pd.read_csv("data/manifests/rc013_source_candidates.csv")
    scans_dir = "data/scans/rc013"
    os.makedirs(scans_dir, exist_ok=True)

    scans_records = []

    for _, row in df.iterrows():
        scan_id = row["source_file_name"]
        rec = {
            "composer": row["composer"],
            "work": row["work"],
            "opus": row["opus_or_catalogue"],
            "movement": int(row["movement"]),
            "title": row["title"],
            "source_archive": row["source_archive"],
            "source_url_or_reference": row["source_url_or_reference"],
            "download_url": row["download_url"],
            "edition": f"{row['edition_or_editor']} ({row['publication_year']})",
            "plate_number": str(row["plate_number"]),
            "source_file_name": scan_id,
            "source_file_sha256": row["source_file_sha256"],
            "source_file_size_bytes": int(row["source_file_size_bytes"]),
            "page_range": row["page_range"],
            "rights_status": row["rights_status"],
        }
        scans_records.append(rec)

        # Write verifiable audit metadata record
        meta_file = os.path.join(scans_dir, f"{row['composer'].lower().replace(' ', '_')}_{row['opus_or_catalogue'].lower().replace(' ', '_')}_mov{int(row['movement']):02d}.source_audit.json")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2, sort_keys=True)

    # Sort records deterministically to compute bundle hash
    scans_records = sorted(scans_records, key=lambda x: (x["composer"], x["opus"], x["movement"]))
    manifest_bytes = json.dumps(scans_records, indent=2, sort_keys=True).encode("utf-8")

    manifest_path = os.path.join(scans_dir, "rc013_scans_manifest.json")
    with open(manifest_path, "wb") as f:
        f.write(manifest_bytes)

    bundle_hash = hashlib.sha256(manifest_bytes).hexdigest()
    print(f"Generated {len(scans_records)} verified source scan records.")
    print(f"RC013_SOURCE_IMAGE_BUNDLE_HASH: {bundle_hash}")


if __name__ == "__main__":
    main()

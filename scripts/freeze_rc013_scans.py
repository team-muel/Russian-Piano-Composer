"""Generates data/scans/rc013 scans manifest and frozen bundle verification."""

from __future__ import annotations

import hashlib
import json
import os

import pandas as pd


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    df = pd.read_csv("data/manifests/rc013_source_candidates.csv")
    scans_dir = "data/scans/rc013"
    os.makedirs(scans_dir, exist_ok=True)

    scans_records = []

    for _, row in df.iterrows():
        scan_id = row["scan_identifier"]
        # Generate canonical scan verification record
        record_content = (
            f"SOURCE_ARCHIVE: {row['source_archive']}\n"
            f"REFERENCE_URL: {row['source_url_or_reference']}\n"
            f"SCAN_IDENTIFIER: {scan_id}\n"
            f"EDITION: {row['edition_or_editor']} ({row['publication_year']})\n"
            f"PAGE_RANGE: {row['page_range']}\n"
            f"WORK: {row['composer']} - {row['work']} {row['opus_or_catalogue']} mov {row['movement']}\n"
            f"RIGHTS: {row['rights_status']}\n"
        ).encode()

        rec_hash = compute_sha256(record_content)
        meta_file = os.path.join(scans_dir, f"{scan_id}.meta")
        with open(meta_file, "wb") as f:
            f.write(record_content)

        scans_records.append({
            "scan_identifier": scan_id,
            "composer": row["composer"],
            "work": row["work"],
            "opus": row["opus_or_catalogue"],
            "movement": int(row["movement"]),
            "sha256": rec_hash,
            "page_range": row["page_range"],
            "source_archive": row["source_archive"],
        })

    # Sort records deterministically to compute bundle hash
    scans_records = sorted(scans_records, key=lambda x: x["scan_identifier"])
    manifest_bytes = json.dumps(scans_records, indent=2, sort_keys=True).encode("utf-8")

    manifest_path = os.path.join(scans_dir, "rc013_scans_manifest.json")
    with open(manifest_path, "wb") as f:
        f.write(manifest_bytes)

    bundle_hash = hashlib.sha256(manifest_bytes).hexdigest()
    print(f"Generated {len(scans_records)} scan metadata records.")
    print(f"RC013_SOURCE_IMAGE_BUNDLE_HASH: {bundle_hash}")


if __name__ == "__main__":
    main()

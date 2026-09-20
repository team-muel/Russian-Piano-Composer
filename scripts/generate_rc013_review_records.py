"""Generates AUTOMATED_QC audit review artifacts for each pilot score in RC-013.

AUTOMATED_QC scope (the only things this generator may certify):
  - Notation-level structural validity (via RC013ScoreValidator)
  - MusicXML parse success
  - Measure count, note count, rest count from MusicXML
  - SHA-256 of the symbolic file at QC time
  - Anti-synthetic guard result

AUTOMATED_QC may NOT claim or assign:
  - source_fidelity_status (requires human source-comparison)
  - measures_fidelity_verified (requires per-measure human review)
  - errors_initial (requires comparison against source scan)
  - unresolved_ambiguities (requires comparison against source scan)

Those fields belong in the per-score source_comparison ledger
(data/reviews/rc013/<score>.source_comparison.json).
"""

from __future__ import annotations

import hashlib
import json
import os
import re

import pandas as pd

from russian_piano_composer.corpus.rc013_validator import RC013ScoreValidator


def compute_sha256_file(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def slugify(text: str) -> str:
    text = text.lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_]", "", text)


def main() -> None:
    df = pd.read_csv("data/manifests/rc013_source_candidates.csv")
    reviews_dir = "data/reviews/rc013"
    os.makedirs(reviews_dir, exist_ok=True)
    validator = RC013ScoreValidator()

    for _, row in df.iterrows():
        comp = row["composer"]
        opus = row["opus_or_catalogue"]
        mov = int(row["movement"])
        fname_opus = opus.lower().replace(" ", "").replace(".", "")
        comp_slug = comp.lower().replace(" ", "_")
        score_file = f"data/scores/rc013/canonical/{comp_slug}_{fname_opus}_no{mov:02d}.musicxml"

        score_sha = compute_sha256_file(score_file)
        report = validator.validate_file(score_file, enforce_anti_synthetic=True)

        # AUTOMATED_QC may only certify properties derivable from the MusicXML itself.
        # Do NOT add: measures_fidelity_verified, source_fidelity_status,
        #             errors_initial, unresolved_ambiguities.
        review_data = {
            "canonical_work_id": f"{comp_slug}_{fname_opus}_m{mov:02d}",
            "composer": comp,
            "opus": opus,
            "movement": mov,
            "title": row["title"],
            "reviewer_type": "AUTOMATED_QC",
            "reviewer_identifier": "rc013_notation_validator_v3",
            "review_date": "2026-09-20",
            "source_file_name": row["source_file_name"],
            "source_file_sha256": row["source_file_sha256"],
            "symbolic_file_path": score_file,
            "symbolic_file_sha256": score_sha,
            # --- Notation-derived properties (AUTOMATED_QC scope) ---
            "measures_in_musicxml": report.num_measures,
            "notes_in_musicxml": report.num_notes,
            "rests_in_musicxml": report.num_rests,
            "notation_errors": [e.to_dict() for e in report.errors],
            "anti_synthetic_guard_passed": report.valid and not any(
                e.code == "SYNTHETIC_REPETITIVE_PATTERN_DETECTED" for e in report.errors
            ),
            # --- Pipeline state (notation QC only) ---
            "pipeline_state": "AUTOMATED_QC_PASS" if report.valid else "AUTOMATED_QC_FAIL",
            # --- Source fidelity: NOT determined by AUTOMATED_QC ---
            "source_fidelity_status": "PENDING_SOURCE_COMPARISON",
            # Source comparison ledger location (not generated here)
            "source_comparison_record": (
                f"{reviews_dir}/{comp_slug}_{fname_opus}_no{mov:02d}.source_comparison.json"
            ),
        }

        out_path = os.path.join(reviews_dir, f"{comp_slug}_{fname_opus}_no{mov:02d}.review.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(review_data, f, indent=2, sort_keys=True)

    print(f"Generated {len(df)} AUTOMATED_QC review records in {reviews_dir}.")
    print("NOTE: source_fidelity_status = PENDING_SOURCE_COMPARISON for all records.")
    print("      Per-measure source comparison must be completed by a human reviewer.")


if __name__ == "__main__":
    main()

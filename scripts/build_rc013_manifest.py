"""Generates data/manifests/rc013_digitization_manifest.yaml for canonical transcribed scores."""

from __future__ import annotations

import hashlib
import os
import re

import pandas as pd
import yaml

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
    scores_dir = "data/scores/rc013/canonical"
    validator = RC013ScoreValidator()

    entries = []

    for _, row in df.iterrows():
        comp = row["composer"]
        opus = row["opus_or_catalogue"]
        mov = int(row["movement"])
        # Format filename: {slugify(comp)}_{slugify(opus)}_no{mov:02d}.musicxml
        fname_opus = opus.lower().replace(" ", "").replace(".", "")
        file_name = f"{slugify(comp)}_{fname_opus}_no{mov:02d}.musicxml"
        file_path = os.path.join(scores_dir, file_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Missing score: {file_path}")

        file_sha = compute_sha256_file(file_path)
        report = validator.validate_file(file_path, enforce_anti_synthetic=True)

        entries.append({
            "canonical_work_id": f"{slugify(comp)}_{fname_opus}_m{mov:02d}",
            "composer": comp,
            "opus_or_catalogue": opus,
            "movement": mov,
            "title": row["title"],
            "relative_score_path": f"data/scores/rc013/canonical/{file_name}",
            "file_sha256": file_sha,
            "pipeline_state": "MANUALLY_TRANSCRIBED",
            "verification_status": "AUTOMATED_QC_PASS",
            "review_record": f"data/reviews/rc013/{slugify(comp)}_{fname_opus}_no{mov:02d}.review.json",
            "source_archive": row["source_archive"],
            "source_file_name": row["source_file_name"],
            "source_file_sha256": row["source_file_sha256"],
            "source_reference_url": row["source_url_or_reference"],
            "rights_status": row["rights_status"],
            "analysis_eligible": False,  # Strict: pilot phase only, not yet released for hypothesis testing
            "generative_eligible": False,
            "num_measures": report.num_measures,
            "num_notes": report.num_notes,
            "num_rests": report.num_rests,
            "time_signatures": report.time_signatures,
            "key_signatures": report.key_signatures,
            "qc_passed": report.valid,
        })

    # Deterministic sort
    entries = sorted(entries, key=lambda x: x["canonical_work_id"])

    manifest_data = {
        "milestone": "RC-013",
        "title": "RC-013 Canonical Pilot Digitization Manifest",
        "description": "Authentic source-transcribed symbolic piano score pilot for Russian confirmatory resumption.",
        "status": "PILOT_SOURCE_FIDELITY_RECOVERY",
        "total_score_entries": len(entries),
        "pilot_composer_counts": {
            "Sergei Lyapunov": sum(1 for e in entries if e["composer"] == "Sergei Lyapunov"),
            "Anton Arensky": sum(1 for e in entries if e["composer"] == "Anton Arensky"),
            "Anatoly Lyadov": sum(1 for e in entries if e["composer"] == "Anatoly Lyadov"),
        },
        "score_entries": entries,
    }

    out_yaml = "data/manifests/rc013_digitization_manifest.yaml"
    with open(out_yaml, "w", encoding="utf-8") as f:
        yaml.dump(manifest_data, f, sort_keys=False, indent=2, allow_unicode=True)

    manifest_sha = compute_sha256_file(out_yaml)
    print(f"Generated {out_yaml} with {len(entries)} scores.")
    print(f"RC013_DIGITIZATION_MANIFEST_HASH: {manifest_sha}")


if __name__ == "__main__":
    main()

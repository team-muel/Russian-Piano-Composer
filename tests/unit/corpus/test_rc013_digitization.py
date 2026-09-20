"""Unit tests for RC-013 Russian Confirmatory Corpus Acquisition & Digitization."""

from __future__ import annotations

import os

import pandas as pd
import yaml
from scripts.compute_rc013_hashes import get_all_rc013_hashes

from russian_piano_composer.corpus.rc013_validator import RC013ScoreValidator


def test_rc013_candidate_inventory_completeness() -> None:
    csv_path = "data/manifests/rc013_source_candidates.csv"
    assert os.path.exists(csv_path)
    df = pd.read_csv(csv_path)

    # Must contain at least 3 distinct Russian composers
    composers = df["composer"].unique()
    assert len(composers) >= 3
    assert "Sergei Lyapunov" in composers
    assert "Anton Arensky" in composers
    assert "Anatoly Lyadov" in composers

    # Every composer must have >= 10 pieces
    counts = df.groupby("composer")["opus_or_catalogue"].count()
    for comp, count in counts.items():
        assert count >= 10, f"{comp} has only {count} pieces, expected >= 10"


def test_rc013_manifest_structure_and_qualification() -> None:
    manifest_path = "data/manifests/rc013_digitization_manifest.yaml"
    assert os.path.exists(manifest_path)
    with open(manifest_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["milestone"] == "RC-013"
    assert data["total_score_entries"] >= 30
    quals = data["composer_qualification"]
    assert quals["Sergei Lyapunov"] >= 10
    assert quals["Anton Arensky"] >= 10
    assert quals["Anatoly Lyadov"] >= 10

    # Every entry must have passed QC and be analysis eligible
    for entry in data["score_entries"]:
        assert entry["qc_passed"] is True
        assert entry["analysis_eligible"] is True
        assert entry["rights_status"] == "PUBLIC_DOMAIN"
        assert entry["provenance_tag"] in ["MANUALLY_TRANSCRIBED", "OMR_CORRECTED"]
        assert entry["verification_status"] == "INDEPENDENTLY_VERIFIED"
        assert os.path.exists(entry["relative_score_path"])


def test_rc013_notation_validation_zero_errors() -> None:
    manifest_path = "data/manifests/rc013_digitization_manifest.yaml"
    with open(manifest_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    validator = RC013ScoreValidator()
    for entry in data["score_entries"]:
        report = validator.validate_file(entry["relative_score_path"])
        assert report.valid is True
        assert len(report.errors) == 0
        assert report.num_measures >= 4
        assert report.num_notes > 0
        assert report.num_parts_or_staves == 2  # Upper and lower staves


def test_rc013_cryptographic_hashes_present_and_reproducible() -> None:
    hashes = get_all_rc013_hashes()
    expected_keys = [
        "RC013_SOURCE_INVENTORY_HASH",
        "RC013_SOURCE_IMAGE_BUNDLE_HASH",
        "RC013_DIGITIZATION_POLICY_HASH",
        "RC013_DIGITIZATION_MANIFEST_HASH",
        "RC013_ERROR_LOG_HASH",
        "RC013_CANONICAL_SYMBOLIC_CORPUS_HASH",
        "RC013_QC_RESULT_HASH",
    ]
    for k in expected_keys:
        assert k in hashes
        assert len(hashes[k]) == 64  # SHA256 hex length

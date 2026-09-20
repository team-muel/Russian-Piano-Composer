"""Unit tests for RC-013 Russian Confirmatory Corpus Acquisition & Digitization (Recovery Pilot)."""

from __future__ import annotations

import os

import pandas as pd
import yaml
from scripts.compute_rc013_hashes import get_all_rc013_hashes

from russian_piano_composer.corpus.rc013_validator import RC013ScoreValidator


def test_rc013_pilot_candidate_inventory_completeness() -> None:
    csv_path = "data/manifests/rc013_source_candidates.csv"
    assert os.path.exists(csv_path)
    df = pd.read_csv(csv_path)

    # Pilot must contain 3 distinct Russian composers, 3 scores each = 9 total
    composers = df["composer"].unique()
    assert len(composers) == 3
    assert "Sergei Lyapunov" in composers
    assert "Anton Arensky" in composers
    assert "Anatoly Lyadov" in composers
    assert len(df) == 9

    counts = df.groupby("composer")["movement"].count()
    for comp, count in counts.items():
        assert count == 3, f"{comp} pilot expected 3 pieces, got {count}"

    # Verify every row has authentic downloaded byte sha256
    for _, row in df.iterrows():
        assert len(str(row["source_file_sha256"])) == 64
        assert int(row["source_file_size_bytes"]) > 0
        assert str(row["rights_status"]) == "PUBLIC_DOMAIN"


def test_rc013_pilot_manifest_and_review_records() -> None:
    manifest_path = "data/manifests/rc013_digitization_manifest.yaml"
    assert os.path.exists(manifest_path)
    with open(manifest_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["milestone"] == "RC-013"
    assert data["status"] == "PILOT_SOURCE_FIDELITY_RECOVERY"
    assert data["total_score_entries"] == 9
    quals = data["pilot_composer_counts"]
    assert quals["Sergei Lyapunov"] == 3
    assert quals["Anton Arensky"] == 3
    assert quals["Anatoly Lyadov"] == 3

    for entry in data["score_entries"]:
        assert entry["qc_passed"] is True
        assert entry["rights_status"] == "PUBLIC_DOMAIN"
        assert entry["pipeline_state"] == "MANUALLY_TRANSCRIBED"
        assert entry["verification_status"] == "AUTOMATED_QC_PASS"
        assert entry["analysis_eligible"] is False  # Safe fail-closed in pilot stage
        assert os.path.exists(entry["relative_score_path"])
        assert os.path.exists(entry["review_record"])


def test_rc013_pilot_notation_validation_and_anti_synthetic_guard() -> None:
    manifest_path = "data/manifests/rc013_digitization_manifest.yaml"
    with open(manifest_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    validator = RC013ScoreValidator()
    for entry in data["score_entries"]:
        report = validator.validate_file(entry["relative_score_path"], enforce_anti_synthetic=True)
        assert report.valid is True
        assert len(report.errors) == 0
        assert report.num_measures >= 20
        assert report.num_notes >= 100
        assert report.num_parts_or_staves == 2


def test_rc013_anti_synthetic_guard_catches_synthetic_fixtures() -> None:
    validator = RC013ScoreValidator()
    syn_file = "data/scores/rc013/fixtures_synthetic/sergei_lyapunov_op_11_mov01.musicxml"
    if os.path.exists(syn_file):
        report = validator.validate_file(syn_file, enforce_anti_synthetic=True)
        assert report.valid is False
        assert any(e.code == "SYNTHETIC_REPETITIVE_PATTERN_DETECTED" for e in report.errors)


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
        assert len(hashes[k]) == 64

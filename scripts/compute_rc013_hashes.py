"""Computes canonical scientific hashes for the RC-013 milestone."""

from __future__ import annotations

import hashlib
import json
import os

import yaml

from russian_piano_composer.corpus.rc013_fidelity import (
    load_canonical_source_manifest,
    validate_source_comparison_ledger,
)
from russian_piano_composer.corpus.rc013_integrity import (
    validate_canonical_score_integrity,
)


def compute_sha256_file(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_normalized_text_sha256(file_path: str) -> str:
    with open(file_path, "rb") as f:
        content = f.read()
    # Canonical line ending normalization: CRLF -> LF, CR -> LF
    normalized = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def compute_directory_bundle_hash(dir_path: str, extension: str = ".musicxml") -> str:
    files = sorted([f for f in os.listdir(dir_path) if f.endswith(extension)])
    bundle_hasher = hashlib.sha256()
    for f in files:
        full_path = os.path.join(dir_path, f)
        file_hash = compute_sha256_file(full_path)
        bundle_hasher.update(f"{f}:{file_hash}\n".encode())
    return bundle_hasher.hexdigest()


def load_canonical_symbolic_paths(manifest_yaml_path: str) -> dict[str, str]:
    """Loads mapping of canonical_work_id to relative_score_path from digitization manifest."""
    mapping: dict[str, str] = {}
    if os.path.exists(manifest_yaml_path):
        with open(manifest_yaml_path, encoding="utf-8") as yf:
            data = yaml.safe_load(yf)
        for entry in data.get("score_entries", []):
            c_id = entry.get("canonical_work_id")
            path = entry.get("relative_score_path")
            if c_id and path:
                mapping[c_id] = path
    return mapping


def compute_source_fidelity_gate_result(
    source_comparison_bundle_hash: str,
    source_img_bundle_hash: str,
    corpus_bundle_hash: str,
    reviews_dir: str = "data/reviews/rc013",
    source_manifest_csv: str = "data/manifests/rc013_source_candidates.csv",
    digitization_manifest_yaml: str = "data/manifests/rc013_digitization_manifest.yaml",
) -> tuple[str, str]:
    """Computes overall pilot source fidelity verdict and gate result hash via production gate."""
    files = sorted([f for f in os.listdir(reviews_dir) if f.endswith(".source_comparison.json")])
    source_sha_map = load_canonical_source_manifest(source_manifest_csv) if os.path.exists(source_manifest_csv) else {}
    sym_path_map = load_canonical_symbolic_paths(digitization_manifest_yaml)

    per_score_records: list[str] = []
    overall_all_verified = bool(files)
    identity_map_path = "data/manifests/rc013_arensky_identity_map.json"
    identity_map_hash = (
        compute_normalized_text_sha256(identity_map_path)
        if os.path.exists(identity_map_path)
        else "MISSING"
    )

    for f in files:
        full_path = os.path.join(reviews_dir, f)
        with open(full_path, encoding="utf-8") as jf:
            ledger_data = json.load(jf)

        score_id = str(ledger_data.get("score_id", f.replace(".source_comparison.json", "")))
        c_work_id = str(ledger_data.get("canonical_work_id", ""))

        # Resolve canonical source SHA
        canonical_source_sha = source_sha_map.get(c_work_id) or source_sha_map.get(score_id)

        # Resolve symbolic file path and current symbolic SHA
        sym_path = sym_path_map.get(c_work_id)
        if not sym_path:
            # Fallback path by score_id
            sym_path = f"data/scores/rc013/canonical/{score_id}.musicxml"

        current_sym_sha = compute_sha256_file(sym_path) if os.path.exists(sym_path) else None

        # Cross-artifact integrity and work identity are prerequisites to fidelity.
        integrity = validate_canonical_score_integrity(
            score_id,
            identity_map_path=identity_map_path,
            digitization_manifest_path=digitization_manifest_yaml,
            reviews_dir=reviews_dir,
            score_path=sym_path,
        )

        if not integrity.artifact_consistent:
            verdict = "CROSS_ARTIFACT_INTEGRITY_FAILED"
            category = (
                integrity.errors[0]
                if integrity.errors
                else "CROSS_ARTIFACT_INTEGRITY_FAILED"
            )
            overall_all_verified = False
        elif integrity.identity_required and not integrity.identity_valid:
            verdict = "IDENTITY_REVALIDATION_REQUIRED"
            category = (
                integrity.errors[0]
                if integrity.errors
                else "IDENTITY_REVALIDATION_REQUIRED"
            )
            overall_all_verified = False
        else:
            res = validate_source_comparison_ledger(
                ledger=ledger_data,
                canonical_source_sha=canonical_source_sha,
                current_symbolic_sha=current_sym_sha,
                fail_fast=False,
            )
            verdict = res.fidelity_status
            category = res.error_category or "NONE"
            if not res.valid:
                overall_all_verified = False

        src_sha_str = canonical_source_sha or "MISSING"
        sym_sha_str = current_sym_sha or "MISSING"
        per_score_records.append(
            f"{score_id}|SRC_SHA:{src_sha_str}|SYM_SHA:{sym_sha_str}|VERDICT:{verdict}|REASON:{category}"
        )

    overall_pilot_verdict = (
        "SOURCE_FIDELITY_VERIFIED" if overall_all_verified else "PENDING_SOURCE_COMPARISON"
    )

    payload_lines = [
        f"SOURCE_COMPARISON_BUNDLE_HASH:{source_comparison_bundle_hash}",
        f"SOURCE_IMAGE_BUNDLE_HASH:{source_img_bundle_hash}",
        f"CANONICAL_SYMBOLIC_CORPUS_HASH:{corpus_bundle_hash}",
        f"IDENTITY_MAP_HASH:{identity_map_hash}",
        f"OVERALL_PILOT_VERDICT:{overall_pilot_verdict}",
        "PER_SCORE_RESULTS:",
        *per_score_records,
    ]

    payload = "\n".join(payload_lines) + "\n"
    gate_result_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return overall_pilot_verdict, gate_result_hash


def get_all_rc013_hashes() -> dict[str, str]:
    # 1. Source Inventory Hash
    source_inv_hash = compute_normalized_text_sha256("data/manifests/rc013_source_candidates.csv")

    # 2. Source Image Bundle Hash
    scans_manifest = "data/scans/rc013/rc013_scans_manifest.json"
    source_img_bundle_hash = compute_sha256_file(scans_manifest)

    # 3. Digitization Policy Hash
    policy_hash = compute_normalized_text_sha256("docs/research/RC013_SCORE_ENTRY_POLICY.md")

    # 4. Digitization Manifest Hash
    manifest_hash = compute_normalized_text_sha256("data/manifests/rc013_digitization_manifest.yaml")

    # 5. Error Log Hash
    error_log_hash = compute_normalized_text_sha256("data/manifests/rc013_error_log.json")

    # 6. Canonical Symbolic Corpus Hash
    corpus_bundle_hash = compute_directory_bundle_hash("data/scores/rc013/canonical", extension=".musicxml")

    # 7. QC Result Hash (combined audit verification of manifest + error log + corpus)
    qc_payload = (
        f"MANIFEST:{manifest_hash}\n"
        f"ERROR_LOG:{error_log_hash}\n"
        f"CORPUS:{corpus_bundle_hash}\n"
    ).encode()
    qc_result_hash = hashlib.sha256(qc_payload).hexdigest()

    # 8. Automated Review Bundle Hash (all *.review.json)
    automated_review_bundle_hash = compute_directory_bundle_hash("data/reviews/rc013", extension=".review.json")

    # 9. Source Comparison Bundle Hash (all *.source_comparison.json)
    source_comparison_bundle_hash = compute_directory_bundle_hash("data/reviews/rc013", extension=".source_comparison.json")

    # 10. Source Fidelity Gate Result Hash (derived from production gate)
    _, source_fidelity_gate_result_hash = compute_source_fidelity_gate_result(
        source_comparison_bundle_hash=source_comparison_bundle_hash,
        source_img_bundle_hash=source_img_bundle_hash,
        corpus_bundle_hash=corpus_bundle_hash,
        reviews_dir="data/reviews/rc013",
        source_manifest_csv="data/manifests/rc013_source_candidates.csv",
        digitization_manifest_yaml="data/manifests/rc013_digitization_manifest.yaml",
    )

    return {
        "RC013_SOURCE_INVENTORY_HASH": source_inv_hash,
        "RC013_SOURCE_IMAGE_BUNDLE_HASH": source_img_bundle_hash,
        "RC013_DIGITIZATION_POLICY_HASH": policy_hash,
        "RC013_DIGITIZATION_MANIFEST_HASH": manifest_hash,
        "RC013_ERROR_LOG_HASH": error_log_hash,
        "RC013_CANONICAL_SYMBOLIC_CORPUS_HASH": corpus_bundle_hash,
        "RC013_QC_RESULT_HASH": qc_result_hash,
        "RC013_AUTOMATED_REVIEW_BUNDLE_HASH": automated_review_bundle_hash,
        "RC013_SOURCE_COMPARISON_BUNDLE_HASH": source_comparison_bundle_hash,
        "RC013_SOURCE_FIDELITY_GATE_RESULT_HASH": source_fidelity_gate_result_hash,
    }


def main() -> None:
    hashes = get_all_rc013_hashes()
    print("==================================================")
    print("   RC-013 Canonical Cryptographic Hashes")
    print("==================================================")
    for k, v in hashes.items():
        print(f"{k}: {v}")
    print("==================================================")


if __name__ == "__main__":
    main()

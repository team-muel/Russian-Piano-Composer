"""Computes canonical scientific hashes for the RC-013 milestone.

Canonical Hash Schema Versions:
- SCHEMA V1: Historical baseline where SOURCE_IMAGE_BUNDLE_HASH hashed only the manifest JSON.
- SCHEMA V2: Hardened canonical baseline where SOURCE_IMAGE_BUNDLE_HASH hashes actual unique authoritative source PDF bytes + manifest binding, and HUMAN_REVIEW_RECEIPT_BUNDLE_HASH hashes validated human review receipts.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

import yaml

from russian_piano_composer.corpus.rc013_fidelity import (
    load_canonical_source_manifest,
    validate_source_comparison_ledger,
)
from russian_piano_composer.corpus.rc013_integrity import (
    validate_canonical_score_integrity,
)
from russian_piano_composer.corpus.rc013_review_ingestion import (
    validate_human_review_receipt,
)

RC013_CANONICAL_HASH_SCHEMA_VERSION: int = 2


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
    if not os.path.exists(dir_path):
        return hashlib.sha256(b"EMPTY_DIRECTORY\n").hexdigest()
    files = sorted([f for f in os.listdir(dir_path) if f.endswith(extension)])
    if not files:
        return hashlib.sha256(b"EMPTY_SET\n").hexdigest()
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


def compute_authoritative_source_image_bundle_hash(
    scans_manifest_path: str = "data/scans/rc013/rc013_scans_manifest.json",
    scans_dir: str = "data/scans/rc013",
) -> str:
    """Computes canonical V2 source image bundle hash from physical authoritative source PDF bytes.

    Fails closed if any declared source PDF is missing or if actual PDF SHA differs from declared SHA.
    """
    if not os.path.exists(scans_manifest_path):
        raise FileNotFoundError(f"SOURCE_MANIFEST_MISSING: {scans_manifest_path}")

    with open(scans_manifest_path, encoding="utf-8") as f:
        scans_manifest: list[dict[str, Any]] = json.load(f)

    # Extract unique source files deterministically
    unique_files: dict[str, str] = {}
    for entry in scans_manifest:
        fn = entry.get("source_file_name")
        declared_sha = entry.get("source_file_sha256")
        if fn and declared_sha and fn not in unique_files:
            unique_files[str(fn)] = str(declared_sha)

    lines: list[str] = []
    for fn in sorted(unique_files.keys()):
        declared_sha = unique_files[fn]
        local_path = os.path.join(scans_dir, fn)
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"SOURCE_BYTES_MISSING: {local_path}")
        actual_sha = compute_sha256_file(local_path)
        if actual_sha != declared_sha:
            raise ValueError(
                f"SOURCE_BYTE_SHA_MISMATCH for {fn}: actual={actual_sha} != declared={declared_sha}"
            )
        lines.append(f"SOURCE_FILE|{fn}|{actual_sha}")

    # Bind the scans manifest file hash
    manifest_file_sha = compute_sha256_file(scans_manifest_path)
    lines.append(f"SCANS_MANIFEST|{manifest_file_sha}")

    payload = "\n".join(lines) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_source_fidelity_gate_result(
    source_comparison_bundle_hash: str,
    source_img_bundle_hash: str,
    corpus_bundle_hash: str,
    reviews_dir: str = "data/reviews/rc013",
    receipts_dir: str = "data/reviews/rc013/accepted",
    source_manifest_csv: str = "data/manifests/rc013_source_candidates.csv",
    digitization_manifest_yaml: str = "data/manifests/rc013_digitization_manifest.yaml",
    packets_dir: str = "data/reviews/rc013/packets",
) -> tuple[str, str]:
    """Computes overall pilot source fidelity verdict and gate result hash via production gate.

    Production fidelity gate requires:
    1. Cross-artifact integrity valid.
    2. Authoritative work identity valid.
    3. Ledger structure and per-measure audit valid.
    4. Valid independent human review receipt present and bound to exact live MusicXML & source PDF bytes.
    """
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

        # 1. Cross-artifact integrity check
        integrity = validate_canonical_score_integrity(
            score_id,
            identity_map_path=identity_map_path,
            digitization_manifest_path=digitization_manifest_yaml,
            reviews_dir=reviews_dir,
            score_path=sym_path,
        )

        # 2. Receipt validation check (Human Review Acceptance Requirement)
        receipt_path = os.path.join(receipts_dir, f"{score_id}.human_review_receipt.json")
        receipt_res = validate_human_review_receipt(
            receipt_path=receipt_path,
            live_symbolic_sha=current_sym_sha or "",
            actual_source_sha=canonical_source_sha or "",
            packets_dir=packets_dir,
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
        elif not receipt_res.valid:
            # Unreviewed / pending independent human review
            verdict = "PENDING_SOURCE_COMPARISON"
            category = "PENDING_INDEPENDENT_HUMAN_REVIEW_RECEIPT"
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

    # 2. Source Image Bundle Hash (V2: actual authoritative PDF bytes + scans manifest binding)
    source_img_bundle_hash = compute_authoritative_source_image_bundle_hash(
        scans_manifest_path="data/scans/rc013/rc013_scans_manifest.json",
        scans_dir="data/scans/rc013",
    )

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

    # 10. Human Review Receipt Bundle Hash (all *.human_review_receipt.json in data/reviews/rc013/accepted)
    human_review_receipt_bundle_hash = compute_directory_bundle_hash(
        "data/reviews/rc013/accepted",
        extension=".human_review_receipt.json",
    )

    # 11. Source Fidelity Gate Result Hash (derived from production gate)
    _, source_fidelity_gate_result_hash = compute_source_fidelity_gate_result(
        source_comparison_bundle_hash=source_comparison_bundle_hash,
        source_img_bundle_hash=source_img_bundle_hash,
        corpus_bundle_hash=corpus_bundle_hash,
        reviews_dir="data/reviews/rc013",
        receipts_dir="data/reviews/rc013/accepted",
        source_manifest_csv="data/manifests/rc013_source_candidates.csv",
        digitization_manifest_yaml="data/manifests/rc013_digitization_manifest.yaml",
        packets_dir="data/reviews/rc013/packets",
    )

    return {
        "RC013_CANONICAL_HASH_SCHEMA_VERSION": str(RC013_CANONICAL_HASH_SCHEMA_VERSION),
        "RC013_SOURCE_INVENTORY_HASH": source_inv_hash,
        "RC013_SOURCE_IMAGE_BUNDLE_HASH": source_img_bundle_hash,
        "RC013_DIGITIZATION_POLICY_HASH": policy_hash,
        "RC013_DIGITIZATION_MANIFEST_HASH": manifest_hash,
        "RC013_ERROR_LOG_HASH": error_log_hash,
        "RC013_CANONICAL_SYMBOLIC_CORPUS_HASH": corpus_bundle_hash,
        "RC013_QC_RESULT_HASH": qc_result_hash,
        "RC013_AUTOMATED_REVIEW_BUNDLE_HASH": automated_review_bundle_hash,
        "RC013_SOURCE_COMPARISON_BUNDLE_HASH": source_comparison_bundle_hash,
        "RC013_HUMAN_REVIEW_RECEIPT_BUNDLE_HASH": human_review_receipt_bundle_hash,
        "RC013_SOURCE_FIDELITY_GATE_RESULT_HASH": source_fidelity_gate_result_hash,
    }


def get_machine_triangulation_hashes() -> dict[str, str]:
    """Computes and returns cryptographic hashes for machine triangulation calibration artifacts (V1, V2, V3, and V4)."""
    manifest_v1_p = "data/manifests/rc013_machine_validation_protocol_v1.json"
    calib_v1_reg_p = "data/calibration/rc013_machine_validation/rc013_calibration_registry.json"
    manifest_v2_p = "data/manifests/rc013_machine_validation_protocol_v2.json"
    calib_v2_reg_p = "data/calibration/rc013_machine_validation/rc013_calibration_v2_registry.json"
    manifest_v3_p = "data/manifests/rc013_machine_validation_protocol_v3.json"
    calib_v3_reg_p = "data/calibration/rc013_machine_validation/rc013_calibration_v3_registry.json"
    manifest_v4_p = "data/manifests/rc013_machine_validation_protocol_v4.json"
    calib_v4_reg_p = "data/calibration/rc013_machine_validation/rc013_calibration_v4_registry.json"
    calib_v4_res_p = "data/reviews/rc013/machine_calibration_v4_result.json"

    res: dict[str, str] = {}

    if os.path.exists(manifest_v1_p):
        with open(manifest_v1_p, encoding="utf-8") as f:
            v1_data = json.load(f)
        calib_v1_corpus_hash = compute_sha256_file(calib_v1_reg_p) if os.path.exists(calib_v1_reg_p) else "0" * 64
        res["RC013_MACHINE_PROTOCOL_V1_HASH"] = v1_data.get("protocol_hash", "")
        res["RC013_CALIBRATION_V1_CORPUS_HASH"] = calib_v1_corpus_hash
        res["RC013_MUTATION_V1_SUITE_HASH"] = v1_data.get("mutation_suite_hash", "")
        res["RC013_CALIBRATION_V1_RESULT_HASH"] = v1_data.get("calibration_result_hash", "")

    if os.path.exists(manifest_v2_p):
        with open(manifest_v2_p, encoding="utf-8") as f:
            v2_data = json.load(f)
        calib_v2_corpus_hash = compute_sha256_file(calib_v2_reg_p) if os.path.exists(calib_v2_reg_p) else "0" * 64
        res["RC013_MACHINE_PROTOCOL_V2_HASH"] = v2_data.get("protocol_hash", "")
        res["RC013_CALIBRATION_V2_CORPUS_HASH"] = calib_v2_corpus_hash
        res["RC013_END_TO_END_MUTATION_SUITE_HASH"] = v2_data.get("end_to_end_mutation_suite_hash", "")
        res["RC013_CALIBRATION_V2_RESULT_HASH"] = v2_data.get("calibration_result_hash", "")

    if os.path.exists(manifest_v3_p):
        with open(manifest_v3_p, encoding="utf-8") as f:
            v3_data = json.load(f)
        calib_v3_corpus_hash = compute_sha256_file(calib_v3_reg_p) if os.path.exists(calib_v3_reg_p) else "0" * 64
        res["RC013_MACHINE_PROTOCOL_V3_HASH"] = v3_data.get("protocol_hash", "")
        res["RC013_CALIBRATION_V3_CORPUS_HASH"] = calib_v3_corpus_hash
        res["RC013_EXTERNAL_ENGINE_BUNDLE_HASH"] = v3_data.get("external_engine_bundle_hash", "")
        res["RC013_REAL_SCAN_BENCHMARK_HASH"] = v3_data.get("real_scan_benchmark_hash", "")
        res["RC013_END_TO_END_MUTATION_V3_HASH"] = v3_data.get("end_to_end_mutation_suite_hash", "")
        res["RC013_CALIBRATION_V3_RESULT_HASH"] = v3_data.get("calibration_result_hash", "")

    if os.path.exists(manifest_v4_p):
        from russian_piano_composer.corpus.rc013_bundle_hashing import (
            compute_calibration_v4_corpus_bundle_hash,
            compute_external_engine_bundle_v4_hash,
            compute_real_scan_benchmark_v4_hash,
        )

        with open(manifest_v4_p, encoding="utf-8") as f:
            v4_data = json.load(f)
        calib_v4_bundle_hash = compute_calibration_v4_corpus_bundle_hash(calib_v4_reg_p)
        ext_v4_hash = compute_external_engine_bundle_v4_hash()
        real_scan_v4_hash = compute_real_scan_benchmark_v4_hash(calib_v4_reg_p)
        calib_v4_res_hash = compute_sha256_file(calib_v4_res_p) if os.path.exists(calib_v4_res_p) else "0" * 64

        res["RC013_MACHINE_PROTOCOL_V4_HASH"] = v4_data.get("protocol_hash", "")
        res["RC013_CALIBRATION_V4_CORPUS_BUNDLE_HASH"] = calib_v4_bundle_hash
        res["RC013_EXTERNAL_ENGINE_BUNDLE_V4_HASH"] = ext_v4_hash
        res["RC013_REAL_SCAN_BENCHMARK_V4_HASH"] = real_scan_v4_hash
        res["RC013_MUTATION_V4_HASH"] = v4_data.get("end_to_end_mutation_suite_hash", "")
        res["RC013_CALIBRATION_V4_RESULT_HASH"] = calib_v4_res_hash

    manifest_v5_p = "data/manifests/rc013_candidate_falsification_protocol_v5.json"
    calib_v5_reg_p = "data/calibration/rc013_machine_validation/rc013_calibration_v5_registry.json"
    calib_v5_res_p = "data/reviews/rc013/candidate_falsification_calibration_v5_result.json"

    if os.path.exists(manifest_v5_p):
        from russian_piano_composer.corpus.rc013_bundle_hashing import (
            compute_calibration_v5_corpus_bundle_hash,
            compute_real_scan_counterfactual_benchmark_hash,
        )

        with open(manifest_v5_p, encoding="utf-8") as f:
            v5_data = json.load(f)
        calib_v5_bundle_hash = compute_calibration_v5_corpus_bundle_hash(calib_v5_reg_p)
        real_scan_v5_hash = compute_real_scan_counterfactual_benchmark_hash(calib_v5_reg_p)
        align_v5_hash = compute_sha256_file("src/russian_piano_composer/corpus/rc013_alignment.py")
        mut_v5_hash = compute_sha256_file("src/russian_piano_composer/corpus/rc013_mutations.py")
        calib_v5_res_hash = compute_sha256_file(calib_v5_res_p) if os.path.exists(calib_v5_res_p) else "0" * 64

        res["RC013_CANDIDATE_FALSIFICATION_PROTOCOL_V5_HASH"] = v5_data.get("protocol_hash", "")
        res["RC013_CANDIDATE_FALSIFICATION_CALIBRATION_CORPUS_HASH"] = calib_v5_bundle_hash
        res["RC013_REAL_SCAN_COUNTERFACTUAL_BENCHMARK_HASH"] = real_scan_v5_hash
        res["RC013_V5_ALIGNMENT_ENGINE_HASH"] = align_v5_hash
        res["RC013_V5_COUNTERFACTUAL_SUITE_HASH"] = mut_v5_hash
        res["RC013_V5_CALIBRATION_RESULT_HASH"] = calib_v5_res_hash

    manifest_v6_p = "data/manifests/rc013_candidate_falsification_protocol_v6.json"
    calib_v6_reg_p = "data/calibration/rc013_machine_validation/rc013_calibration_v6_registry.json"
    calib_v6_res_p = "data/reviews/rc013/candidate_falsification_calibration_v6_result.json"
    bench_v6_dir = "data/reviews/rc013/candidate_falsification_v6_benchmark"

    if os.path.exists(manifest_v6_p):
        from russian_piano_composer.corpus.rc013_bundle_hashing import (
            compute_calibration_v6_corpus_bundle_hash,
            compute_v6_counterfactual_benchmark_bundle_hash,
        )

        with open(manifest_v6_p, encoding="utf-8") as f:
            v6_data = json.load(f)
        calib_v6_bundle_hash = compute_calibration_v6_corpus_bundle_hash(calib_v6_reg_p)
        bench_v6_bundle_hash = compute_v6_counterfactual_benchmark_bundle_hash(bench_v6_dir)
        align_v6_hash = compute_sha256_file("src/russian_piano_composer/corpus/rc013_alignment.py")
        metric_v6_hash = compute_sha256_file("src/russian_piano_composer/corpus/rc013_falsification_protocol.py")
        audit_56_hash = compute_sha256_file("src/russian_piano_composer/corpus/rc013_feature_dependency.py")
        calib_v6_res_hash = compute_sha256_file(calib_v6_res_p) if os.path.exists(calib_v6_res_p) else "0" * 64

        res["RC013_CANDIDATE_FALSIFICATION_PROTOCOL_V6_HASH"] = v6_data.get("protocol_hash", "")
        res["RC013_V6_CALIBRATION_CORPUS_HASH"] = calib_v6_bundle_hash
        res["RC013_V6_COUNTERFACTUAL_BENCHMARK_BUNDLE_HASH"] = bench_v6_bundle_hash
        res["RC013_V6_ALIGNMENT_ENGINE_HASH"] = align_v6_hash
        res["RC013_V6_DIFFERENTIAL_METRIC_HASH"] = metric_v6_hash
        res["RC013_V6_DESCRIPTOR_DEPENDENCY_AUDIT_HASH"] = audit_56_hash
        res["RC013_V6_CALIBRATION_RESULT_HASH"] = calib_v6_res_hash

    return res


def main() -> None:
    hashes = get_all_rc013_hashes()
    print("==================================================")
    print(f"   RC-013 Canonical Hashes (Schema V{RC013_CANONICAL_HASH_SCHEMA_VERSION})")
    print("==================================================")
    for k, v in hashes.items():
        print(f"{k}: {v}")
    print("==================================================")

    mach_hashes = get_machine_triangulation_hashes()
    if mach_hashes:
        print("\n==================================================")
        print("   RC-013 Machine Validation Protocol Hashes")
        print("==================================================")
        for k, v in mach_hashes.items():
            print(f"{k}: {v}")
        print("==================================================")


if __name__ == "__main__":
    main()

"""Computes canonical scientific hashes for the RC-013 milestone."""

from __future__ import annotations

import hashlib
import json
import os


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


def compute_source_fidelity_gate_result(
    source_comparison_bundle_hash: str,
    source_img_bundle_hash: str,
    corpus_bundle_hash: str,
    reviews_dir: str = "data/reviews/rc013",
) -> tuple[str, str]:
    """Computes overall pilot source fidelity verdict and the gate result hash."""
    files = sorted([f for f in os.listdir(reviews_dir) if f.endswith(".source_comparison.json")])
    per_score_verdicts: list[str] = []
    overall_all_verified = bool(files)

    for f in files:
        full_path = os.path.join(reviews_dir, f)
        with open(full_path, encoding="utf-8") as jf:
            ledger_data = json.load(jf)
        verdict = ledger_data.get("summary", {}).get("source_fidelity_verdict", "PENDING_SOURCE_COMPARISON")
        score_id = ledger_data.get("score_id", f)
        per_score_verdicts.append(f"{score_id}:{verdict}")
        if verdict != "SOURCE_FIDELITY_VERIFIED":
            overall_all_verified = False

    overall_pilot_verdict = (
        "SOURCE_FIDELITY_VERIFIED" if overall_all_verified else "PENDING_SOURCE_COMPARISON"
    )

    payload_lines = [
        f"SOURCE_COMPARISON_BUNDLE_HASH:{source_comparison_bundle_hash}",
        f"SOURCE_IMAGE_BUNDLE_HASH:{source_img_bundle_hash}",
        f"CANONICAL_SYMBOLIC_CORPUS_HASH:{corpus_bundle_hash}",
        f"OVERALL_PILOT_VERDICT:{overall_pilot_verdict}",
        "PER_SCORE_VERDICTS:",
        *per_score_verdicts,
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

    # 10. Source Fidelity Gate Result Hash
    _, source_fidelity_gate_result_hash = compute_source_fidelity_gate_result(
        source_comparison_bundle_hash=source_comparison_bundle_hash,
        source_img_bundle_hash=source_img_bundle_hash,
        corpus_bundle_hash=corpus_bundle_hash,
        reviews_dir="data/reviews/rc013",
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

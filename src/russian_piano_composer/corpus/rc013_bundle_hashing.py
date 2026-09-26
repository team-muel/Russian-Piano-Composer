"""Deterministic Bundle and Infrastructure Hashing for RC-013 Machine Verification Protocols.

Provides deterministic canonical hashes across:
- Protocol V1, V2, V3, V4, V5, and V6 calibration corpora, engine bundles, benchmark suites, and results.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
from typing import Any


def compute_file_sha256(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_directory_bundle_hash(dir_path: str, extension: str = ".json") -> str:
    if not os.path.exists(dir_path):
        return hashlib.sha256(b"EMPTY_DIRECTORY\n").hexdigest()
    files = sorted([f for f in os.listdir(dir_path) if f.endswith(extension)])
    if not files:
        return hashlib.sha256(b"EMPTY_SET\n").hexdigest()
    bundle_hasher = hashlib.sha256()
    for f in files:
        full_path = os.path.join(dir_path, f)
        file_hash = compute_file_sha256(full_path)
        bundle_hasher.update(f"{f}:{file_hash}\n".encode())
    return bundle_hasher.hexdigest()


def compute_calibration_v4_corpus_bundle_hash(
    registry_path: str = "data/calibration/rc013_machine_validation/rc013_calibration_v4_registry.json",
) -> str:
    """Computes a deterministic byte bundle over all calibration PDFs, scans, and scores declared in registry."""
    if not os.path.exists(registry_path):
        return "0" * 64

    with open(registry_path, encoding="utf-8") as f:
        registry: list[dict[str, Any]] = json.load(f)

    bundle_hasher = hashlib.sha256()
    # Sort entries by artifact_id
    for entry in sorted(registry, key=lambda x: x["artifact_id"]):
        s_id = entry["artifact_id"]
        gt_path = entry.get("ground_truth_path", "")
        gt_sha = compute_file_sha256(gt_path) if os.path.exists(gt_path) else "MISSING"

        pdf_path = entry.get("historical_pdf_path", "")
        pdf_sha = compute_file_sha256(pdf_path) if pdf_path and os.path.exists(pdf_path) else "NO_PDF"

        img_shas: list[str] = []
        for img_p in entry.get("historical_page_image_paths", []):
            if os.path.exists(img_p):
                img_shas.append(f"{os.path.basename(img_p)}:{compute_file_sha256(img_p)}")
            else:
                img_shas.append(f"{os.path.basename(img_p)}:MISSING")

        entry_line = f"{s_id}|GT:{gt_sha}|PDF:{pdf_sha}|IMGS:{','.join(img_shas)}\n"
        bundle_hasher.update(entry_line.encode())

    return bundle_hasher.hexdigest()


def compute_external_engine_bundle_v4_hash() -> str:
    """Computes deterministic hash over external Audiveris, homr, and MuseScore executable/binary assets."""
    bundle_hasher = hashlib.sha256()

    # 1. MuseScore 4
    mscore_p = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
    if os.path.exists(mscore_p):
        bundle_hasher.update(f"MUSESCORE4:{compute_file_sha256(mscore_p)}\n".encode())
    else:
        bundle_hasher.update(b"MUSESCORE4:MISSING\n")

    # 2. Audiveris CLI
    audiveris_p = r"C:\Users\User\AppData\Local\Programs\Audiveris\bin\Audiveris.bat"
    if os.path.exists(audiveris_p):
        bundle_hasher.update(f"AUDIVERIS:{compute_file_sha256(audiveris_p)}\n".encode())
    else:
        bundle_hasher.update(b"AUDIVERIS:MISSING\n")

    # 3. homr model ONNX weights
    try:
        import homr

        pkg_root = os.path.dirname(homr.__file__)
        for onnx_p in sorted(glob.glob(os.path.join(pkg_root, "*.onnx"))):
            bundle_hasher.update(f"HOMR_MODEL:{os.path.basename(onnx_p)}:{compute_file_sha256(onnx_p)}\n".encode())
    except ImportError:
        bundle_hasher.update(b"HOMR:MISSING\n")

    return bundle_hasher.hexdigest()


def compute_real_scan_benchmark_v4_hash(
    registry_path: str = "data/calibration/rc013_machine_validation/rc013_calibration_v4_registry.json",
) -> str:
    """Computes deterministic hash over real-scan benchmark source PDFs, selected page mappings, and ground-truth scores."""
    if not os.path.exists(registry_path):
        return "0" * 64

    with open(registry_path, encoding="utf-8") as f:
        registry: list[dict[str, Any]] = json.load(f)

    real_entries = [e for e in registry if e.get("provenance_class") == "REAL_HISTORICAL_SCAN"]
    bundle_hasher = hashlib.sha256()

    for e in sorted(real_entries, key=lambda x: x["artifact_id"]):
        s_id = e["artifact_id"]
        pdf_sha = e.get("historical_pdf_sha256", "")
        gt_sha = e.get("ground_truth_sha256", "")
        page_indices = str(e.get("historical_pdf_page_indices", []))
        img_shas = ",".join(e.get("historical_page_image_sha256s", []))
        payload = f"{s_id}|PDF:{pdf_sha}|PAGES:{page_indices}|IMGS:{img_shas}|GT:{gt_sha}\n"
        bundle_hasher.update(payload.encode())

    return bundle_hasher.hexdigest()


def compute_calibration_v5_corpus_bundle_hash(
    registry_path: str = "data/calibration/rc013_machine_validation/rc013_calibration_v5_registry.json",
) -> str:
    """Computes a deterministic byte bundle over Protocol V5 registry, PDFs, scans, and scores."""
    return compute_calibration_v4_corpus_bundle_hash(registry_path=registry_path)


def compute_real_scan_counterfactual_benchmark_hash(
    registry_path: str = "data/calibration/rc013_machine_validation/rc013_calibration_v5_registry.json",
) -> str:
    """Computes deterministic hash over real-scan counterfactual benchmark suite."""
    return compute_real_scan_benchmark_v4_hash(registry_path=registry_path)


def compute_calibration_v6_corpus_bundle_hash(
    registry_path: str = "data/calibration/rc013_machine_validation/rc013_calibration_v6_registry.json",
) -> str:
    """Computes a deterministic byte bundle over Protocol V6 registry, PDFs, scans, and scores."""
    return compute_calibration_v4_corpus_bundle_hash(registry_path=registry_path)


def compute_v6_counterfactual_benchmark_bundle_hash(
    benchmark_dir: str = "data/reviews/rc013/candidate_falsification_v6_benchmark",
) -> str:
    """Computes deterministic hash over persisted Protocol V6 benchmark specimen JSON files."""
    return compute_directory_bundle_hash(benchmark_dir, extension=".json")

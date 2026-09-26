"""Calculates deterministic byte bundles and execution hashes for Protocol V4 machine validation."""

from __future__ import annotations

import glob
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def compute_file_sha256(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_calibration_v4_corpus_bundle_hash(
    registry_path: str = "data/calibration/rc013_machine_validation/rc013_calibration_v4_registry.json",
) -> str:
    """Computes a deterministic byte bundle over registry, historical PDFs, scan images, MSCX scores, and MusicXML scores."""
    if not os.path.exists(registry_path):
        return "0" * 64

    with open(registry_path, encoding="utf-8") as f:
        registry: list[dict[str, Any]] = json.load(f)

    bundle_hasher = hashlib.sha256()
    reg_bytes = Path(registry_path).read_bytes()
    bundle_hasher.update(f"REGISTRY:{hashlib.sha256(reg_bytes).hexdigest()}\n".encode())

    # Collect unique physical files
    unique_files: dict[str, str] = {}
    for entry in registry:
        gt_p = entry.get("ground_truth_path")
        if gt_p and os.path.exists(gt_p):
            unique_files[os.path.normpath(gt_p)] = compute_file_sha256(gt_p)

        pdf_p = entry.get("historical_pdf_path")
        if pdf_p and os.path.exists(pdf_p):
            unique_files[os.path.normpath(pdf_p)] = compute_file_sha256(pdf_p)

        for img_p in entry.get("historical_page_image_paths", []):
            if img_p and os.path.exists(img_p):
                unique_files[os.path.normpath(img_p)] = compute_file_sha256(img_p)

    for p in sorted(unique_files.keys()):
        bundle_hasher.update(f"{p}:{unique_files[p]}\n".encode())

    return bundle_hasher.hexdigest()


def compute_external_engine_bundle_v4_hash(
    audiveris_exe: str = r"tools\audiveris\Audiveris\Audiveris.exe",
    java_exe: str = r"tools\jdk-17.0.14+7\bin\java.exe",
    musescore_exe: str = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
) -> str:
    """Computes deterministic hash over external engine binaries, runtimes, and neural ONNX model weights."""
    bundle_hasher = hashlib.sha256()

    if os.path.exists(audiveris_exe):
        bundle_hasher.update(f"AUDIVERIS_EXE:{compute_file_sha256(audiveris_exe)}\n".encode())
    else:
        bundle_hasher.update(b"AUDIVERIS_EXE:MISSING\n")

    if os.path.exists(java_exe):
        bundle_hasher.update(f"JAVA_EXE:{compute_file_sha256(java_exe)}\n".encode())
    else:
        bundle_hasher.update(b"JAVA_EXE:MISSING\n")

    if os.path.exists(musescore_exe):
        bundle_hasher.update(f"MUSESCORE_EXE:{compute_file_sha256(musescore_exe)}\n".encode())
    else:
        bundle_hasher.update(b"MUSESCORE_EXE:MISSING\n")

    # homr ONNX models
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


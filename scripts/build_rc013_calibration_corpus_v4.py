"""Downloader and builder for full-movement multi-page external piano calibration benchmark corpus (Protocol V4)."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import urllib.request
from typing import Any

import pypdfium2 as pdfium


def compute_file_sha256(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


CALIB_V4_DIR = "data/calibration/rc013_machine_validation"
SCORES_DIR = os.path.join(CALIB_V4_DIR, "scores")
SCANS_DIR = os.path.join(CALIB_V4_DIR, "scans")
HISTORICAL_SCANS_DIR = os.path.join(CALIB_V4_DIR, "historical_scans")
PDFS_DIR = os.path.join(CALIB_V4_DIR, "historical_pdfs")
RENDERED_DIR = os.path.join(CALIB_V4_DIR, "rendered_production")

MUSESCORE_EXE = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"

# External DCMLab Full-Movement Piano Targets
EXTERNAL_V4_TARGETS = [
    {
        "artifact_id": "chopin_mazurka_op06_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in F-sharp minor, Op. 6 No. 1",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "dataset_version": "main",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Joseffy edition 1915)",
        "mscx_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/MS3/BI60-1op06-1.mscx",
        "pdf_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/pdf/IMSLP111835-PMLP02286-FChopin_Mazurkas%2C_Op.6_Joseffy.pdf",
        "pdf_filename": "chopin_mazurka_op06_no01_source.pdf",
        "historical_pdf_page_indices": [0, 1, 2],
        "historical_printed_pages": ["3", "4", "5"],
        "movement_page_count": 3,
        "measures_total": 75,
        "first_source_measure": 1,
        "last_source_measure": 75,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 75,
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
    },
    {
        "artifact_id": "chopin_mazurka_op07_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in B-flat major, Op. 7 No. 1",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "dataset_version": "main",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Joseffy edition 1915)",
        "mscx_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/MS3/BI61-1op07-1.mscx",
        "pdf_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/pdf/IMSLP111837-PMLP02289-FChopin_Mazurkas%2C_Op.7_Joseffy.pdf",
        "pdf_filename": "chopin_mazurka_op07_no01_source.pdf",
        "historical_pdf_page_indices": [0, 1],
        "historical_printed_pages": ["12", "13"],
        "movement_page_count": 2,
        "measures_total": 67,
        "first_source_measure": 1,
        "last_source_measure": 67,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 67,
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
    },
    {
        "artifact_id": "chopin_mazurka_op17_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in B-flat major, Op. 17 No. 1",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "dataset_version": "main",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Joseffy edition 1915)",
        "mscx_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/MS3/BI77-1op17-1.mscx",
        "pdf_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/pdf/IMSLP111838-PMLP02281-FChopin_Mazurkas%2C_Op.17_Joseffy.pdf",
        "pdf_filename": "chopin_mazurka_op17_no01_source.pdf",
        "historical_pdf_page_indices": [0, 1],
        "historical_printed_pages": ["22", "23"],
        "movement_page_count": 2,
        "measures_total": 61,
        "first_source_measure": 1,
        "last_source_measure": 61,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 61,
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
    },
    {
        "artifact_id": "grieg_lyric_pieces_op12_no01",
        "composer": "Edvard Grieg",
        "work": "Arietta, Lyric Pieces Op. 12 No. 1",
        "dataset_name": "DCMLab/grieg_lyric_pieces",
        "dataset_version": "main",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (C. F. Peters Gesamtausgabe)",
        "mscx_url": "https://raw.githubusercontent.com/DCMLab/grieg_lyric_pieces/main/MS3/op12n01.mscx",
        "pdf_url": "https://raw.githubusercontent.com/DCMLab/grieg_lyric_pieces/main/pdf/GA%20Bd.%201%2C%20Heft%20I%20op.%2012.pdf",
        "pdf_filename": "grieg_lyric_pieces_op12_source.pdf",
        "historical_pdf_page_indices": [0],
        "historical_printed_pages": ["1"],
        "movement_page_count": 1,
        "measures_total": 23,
        "first_source_measure": 1,
        "last_source_measure": 23,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 23,
        "split": "CALIBRATION_V4_FINAL_HOLDOUT",
        "provenance_class": "REAL_HISTORICAL_SCAN",
    },
]

# Synthetic controlled baselines
SYNTHETIC_TARGETS = [
    {
        "artifact_id": "chopin_op28_no07",
        "composer": "Frédéric Chopin",
        "work": "Prélude in A major, Op. 28 No. 7",
        "score_type": "piano_solo",
        "measures_total": 16,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/chopin_op28_no07.musicxml",
        "image_paths": ["data/calibration/rc013_machine_validation/scans/chopin_op28_no07_p1.png"],
        "historical_page_indices": [0],
        "historical_printed_pages": ["1"],
        "movement_page_count": 1,
        "split": "SYNTHETIC_CONTROLLED_CALIBRATION",
        "provenance_class": "SYNTHETIC_DEGRADED_RENDER",
        "dataset_name": "In-Repository Controlled Synthetic Benchmark",
        "digital_dataset_license": "PUBLIC_DOMAIN",
        "historical_scan_status": "SYNTHETIC_VECTOR_RENDER",
    },
    {
        "artifact_id": "chopin_op28_no20",
        "composer": "Frédéric Chopin",
        "work": "Prélude in C minor, Op. 28 No. 20",
        "score_type": "piano_solo",
        "measures_total": 13,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/chopin_op28_no20.musicxml",
        "image_paths": ["data/calibration/rc013_machine_validation/scans/chopin_op28_no20_p1.png"],
        "historical_page_indices": [0],
        "historical_printed_pages": ["1"],
        "movement_page_count": 1,
        "split": "SYNTHETIC_CONTROLLED_CALIBRATION",
        "provenance_class": "SYNTHETIC_DEGRADED_RENDER",
        "dataset_name": "In-Repository Controlled Synthetic Benchmark",
        "digital_dataset_license": "PUBLIC_DOMAIN",
        "historical_scan_status": "SYNTHETIC_VECTOR_RENDER",
    },
    {
        "artifact_id": "bach_bwv846_prelude",
        "composer": "Johann Sebastian Bach",
        "work": "Prelude in C major, BWV 846",
        "score_type": "piano_solo",
        "measures_total": 35,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/bach_bwv846_prelude.musicxml",
        "image_paths": ["data/calibration/rc013_machine_validation/scans/bach_bwv846_prelude_p1.png"],
        "historical_page_indices": [0],
        "historical_printed_pages": ["1"],
        "movement_page_count": 1,
        "split": "SYNTHETIC_CONTROLLED_CALIBRATION",
        "provenance_class": "SYNTHETIC_DEGRADED_RENDER",
        "dataset_name": "In-Repository Controlled Synthetic Benchmark",
        "digital_dataset_license": "PUBLIC_DOMAIN",
        "historical_scan_status": "SYNTHETIC_VECTOR_RENDER",
    },
]


def download_file_with_retry(url: str, dest_path: str) -> None:
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Python-urllib-Russian-Piano-Composer"})
    with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())


def convert_mscx_to_musicxml(mscx_path: str, output_xml_path: str) -> None:
    cmd = [MUSESCORE_EXE, os.path.abspath(mscx_path), "-o", os.path.abspath(output_xml_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(output_xml_path):
        raise RuntimeError(f"MuseScore conversion failed for {mscx_path}: {res.stderr}")


def extract_scan_pages_from_pdf(pdf_path: str, page_indices: list[int], output_png_prefix: str, dpi: int = 300) -> list[str]:
    pdf = pdfium.PdfDocument(pdf_path)
    output_paths: list[str] = []
    for idx, p_num in enumerate(page_indices):
        page = pdf[p_num]
        image = page.render(scale=dpi / 72.0).to_pil()
        out_p = f"{output_png_prefix}_p{idx + 1}.png"
        os.makedirs(os.path.dirname(out_p), exist_ok=True)
        image.save(out_p, "PNG")
        output_paths.append(out_p)
    return output_paths


def build_v4_registry() -> list[dict[str, Any]]:
    os.makedirs(SCORES_DIR, exist_ok=True)
    os.makedirs(SCANS_DIR, exist_ok=True)
    os.makedirs(HISTORICAL_SCANS_DIR, exist_ok=True)
    os.makedirs(PDFS_DIR, exist_ok=True)
    os.makedirs(RENDERED_DIR, exist_ok=True)

    registry: list[dict[str, Any]] = []

    # 1. Process Synthetic Targets
    for syn in SYNTHETIC_TARGETS:
        gt_p = syn["ground_truth_path"]
        img_ps = syn["image_paths"]
        entry = {
            "artifact_id": syn["artifact_id"],
            "composer": syn["composer"],
            "work": syn["work"],
            "score_type": syn["score_type"],
            "measures_total": syn["measures_total"],
            "ground_truth_path": gt_p,
            "ground_truth_sha256": compute_file_sha256(gt_p),
            "historical_page_indices": syn["historical_page_indices"],
            "historical_printed_pages": syn["historical_printed_pages"],
            "movement_page_count": syn["movement_page_count"],
            "historical_page_image_paths": img_ps,
            "historical_page_image_sha256s": [compute_file_sha256(p) for p in img_ps],
            "split": syn["split"],
            "provenance_class": syn["provenance_class"],
            "dataset_name": syn["dataset_name"],
            "digital_dataset_license": syn["digital_dataset_license"],
            "historical_scan_status": syn["historical_scan_status"],
        }
        registry.append(entry)

    # 2. Process Real-Scan Targets
    for tgt in EXTERNAL_V4_TARGETS:
        score_id = tgt["artifact_id"]
        mscx_path = os.path.join(SCORES_DIR, f"{score_id}.mscx")
        xml_path = os.path.join(SCORES_DIR, f"{score_id}.musicxml")
        pdf_path = os.path.join(PDFS_DIR, tgt["pdf_filename"])

        download_file_with_retry(tgt["mscx_url"], mscx_path)
        download_file_with_retry(tgt["pdf_url"], pdf_path)
        convert_mscx_to_musicxml(mscx_path, xml_path)

        png_prefix = os.path.join(HISTORICAL_SCANS_DIR, score_id)
        img_paths = extract_scan_pages_from_pdf(pdf_path, tgt["historical_pdf_page_indices"], png_prefix)

        entry = {
            "artifact_id": score_id,
            "composer": tgt["composer"],
            "work": tgt["work"],
            "score_type": "piano_solo",
            "measures_total": tgt["measures_total"],
            "ground_truth_path": xml_path,
            "ground_truth_sha256": compute_file_sha256(xml_path),
            "historical_pdf_path": pdf_path,
            "historical_pdf_sha256": compute_file_sha256(pdf_path),
            "historical_pdf_page_indices": tgt["historical_pdf_page_indices"],
            "historical_printed_pages": tgt["historical_printed_pages"],
            "movement_page_count": tgt["movement_page_count"],
            "historical_page_image_paths": img_paths,
            "historical_page_image_sha256s": [compute_file_sha256(p) for p in img_paths],
            "first_source_measure": tgt["first_source_measure"],
            "last_source_measure": tgt["last_source_measure"],
            "first_ground_truth_measure": tgt["first_ground_truth_measure"],
            "last_ground_truth_measure": tgt["last_ground_truth_measure"],
            "split": tgt["split"],
            "provenance_class": tgt["provenance_class"],
            "dataset_name": tgt["dataset_name"],
            "dataset_version": tgt["dataset_version"],
            "digital_dataset_license": tgt["digital_dataset_license"],
            "historical_scan_status": tgt["historical_scan_status"],
            "upstream_mscx_url": tgt["mscx_url"],
            "upstream_pdf_url": tgt["pdf_url"],
        }
        registry.append(entry)

    registry_path = os.path.join(CALIB_V4_DIR, "rc013_calibration_v4_registry.json")
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
        f.write("\n")

    print(f"Protocol V4 Calibration Registry created at: {registry_path}")
    print(f"Total entries: {len(registry)}")
    return registry


if __name__ == "__main__":
    build_v4_registry()

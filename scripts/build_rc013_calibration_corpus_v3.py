"""Downloader and builder for genuine external real-scan piano calibration benchmark corpus (DCMLab)."""

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


CALIB_V3_DIR = "data/calibration/rc013_machine_validation"
SCORES_DIR = os.path.join(CALIB_V3_DIR, "scores")
SCANS_DIR = os.path.join(CALIB_V3_DIR, "scans")
HISTORICAL_SCANS_DIR = os.path.join(CALIB_V3_DIR, "historical_scans")
PDFS_DIR = os.path.join(CALIB_V3_DIR, "historical_pdfs")
RENDERED_DIR = os.path.join(CALIB_V3_DIR, "rendered_production")

MUSESCORE_EXE = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"

# External DCMLab Chopin Mazurkas configuration
EXTERNAL_TARGETS = [
    {
        "artifact_id": "chopin_mazurka_op06_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in F-sharp minor, Op. 6 No. 1",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "mscx_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/MS3/BI60-1op06-1.mscx",
        "pdf_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/pdf/IMSLP111835-PMLP02286-FChopin_Mazurkas%2C_Op.6_Joseffy.pdf",
        "pdf_page_index": 2,  # 0-indexed page in the Joseffy edition corresponding to Op. 6 No. 1
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "license": "CC BY-SA 4.0 (annotations) / Public Domain (Joseffy historical first/early edition)",
    },
    {
        "artifact_id": "chopin_mazurka_op07_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in B-flat major, Op. 7 No. 1",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "mscx_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/MS3/BI61-1op07-1.mscx",
        "pdf_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/pdf/IMSLP111837-PMLP02289-FChopin_Mazurkas%2C_Op.7_Joseffy.pdf",
        "pdf_page_index": 2,
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "license": "CC BY-SA 4.0 (annotations) / Public Domain (Joseffy historical edition)",
    },
    {
        "artifact_id": "chopin_mazurka_op17_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in B-flat major, Op. 17 No. 1",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "mscx_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/MS3/BI77-1op17-1.mscx",
        "pdf_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/pdf/IMSLP111838-PMLP02281-FChopin_Mazurkas%2C_Op.17_Joseffy.pdf",
        "pdf_page_index": 2,
        "split": "CALIBRATION_V3_FINAL_HOLDOUT",
        "license": "CC BY-SA 4.0 (annotations) / Public Domain (Joseffy historical edition)",
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


def extract_scan_page_from_pdf(pdf_path: str, page_idx: int, output_png_path: str, dpi: int = 300) -> None:
    pdf = pdfium.PdfDocument(pdf_path)
    page = pdf[page_idx]
    image = page.render(scale=dpi / 72.0).to_pil()
    os.makedirs(os.path.dirname(output_png_path), exist_ok=True)
    image.save(output_png_path, "PNG")


def main() -> None:
    os.makedirs(SCORES_DIR, exist_ok=True)
    os.makedirs(SCANS_DIR, exist_ok=True)
    os.makedirs(HISTORICAL_SCANS_DIR, exist_ok=True)
    os.makedirs(PDFS_DIR, exist_ok=True)
    os.makedirs(RENDERED_DIR, exist_ok=True)

    v3_registry: list[dict[str, Any]] = []

    # 1. Include synthetic controlled items with accurate SYNTHETIC_CONTROLLED_CALIBRATION provenance
    synthetic_items = [
        {
            "artifact_id": "chopin_op28_no07",
            "composer": "Frédéric Chopin",
            "work": "Prélude in A major, Op. 28 No. 7",
            "score_type": "piano_solo",
            "measures_total": 16,
            "ground_truth_path": "data/calibration/rc013_machine_validation/scores/chopin_op28_no07.musicxml",
            "image_path": "data/calibration/rc013_machine_validation/scans/chopin_op28_no07_p1.png",
            "split": "SYNTHETIC_CONTROLLED_CALIBRATION",
            "provenance_class": "SYNTHETIC_DEGRADED_RENDER",
            "dataset_name": "In-Repository Controlled Synthetic Benchmark",
            "license": "PUBLIC_DOMAIN / MUTOPIA",
        },
        {
            "artifact_id": "chopin_op28_no20",
            "composer": "Frédéric Chopin",
            "work": "Prélude in C minor, Op. 28 No. 20",
            "score_type": "piano_solo",
            "measures_total": 13,
            "ground_truth_path": "data/calibration/rc013_machine_validation/scores/chopin_op28_no20.musicxml",
            "image_path": "data/calibration/rc013_machine_validation/scans/chopin_op28_no20_p1.png",
            "split": "SYNTHETIC_CONTROLLED_CALIBRATION",
            "provenance_class": "SYNTHETIC_DEGRADED_RENDER",
            "dataset_name": "In-Repository Controlled Synthetic Benchmark",
            "license": "PUBLIC_DOMAIN / MUTOPIA",
        },
        {
            "artifact_id": "bach_bwv846_prelude",
            "composer": "Johann Sebastian Bach",
            "work": "Prelude in C major, BWV 846",
            "score_type": "piano_solo",
            "measures_total": 35,
            "ground_truth_path": "data/calibration/rc013_machine_validation/scores/bach_bwv846_prelude.musicxml",
            "image_path": "data/calibration/rc013_machine_validation/scans/bach_bwv846_prelude_p1.png",
            "split": "SYNTHETIC_CONTROLLED_CALIBRATION",
            "provenance_class": "SYNTHETIC_DEGRADED_RENDER",
            "dataset_name": "In-Repository Controlled Synthetic Benchmark",
            "license": "PUBLIC_DOMAIN / MUTOPIA",
        },
    ]

    for item in synthetic_items:
        item["ground_truth_sha256"] = compute_file_sha256(item["ground_truth_path"])
        item["image_sha256"] = compute_file_sha256(item["image_path"])
        v3_registry.append(item)

    # 2. Acquire and process external real-scan calibration targets (DCMLab)
    print("--- Acquiring External Real-Scan Calibration Targets from DCMLab ---")
    for tgt in EXTERNAL_TARGETS:
        score_id = tgt["artifact_id"]
        mscx_fn = f"{score_id}.mscx"
        mscx_path = os.path.join(SCORES_DIR, mscx_fn)
        xml_path = os.path.join(SCORES_DIR, f"{score_id}.musicxml")
        pdf_fn = f"{score_id}_source.pdf"
        pdf_path = os.path.join(PDFS_DIR, pdf_fn)
        scan_png_path = os.path.join(HISTORICAL_SCANS_DIR, f"{score_id}_p1.png")

        print(f"Downloading {score_id} MSCX and PDF...")
        download_file_with_retry(tgt["mscx_url"], mscx_path)
        download_file_with_retry(tgt["pdf_url"], pdf_path)

        print(f"Converting MSCX to MusicXML via MuseScore CLI: {xml_path}")
        convert_mscx_to_musicxml(mscx_path, xml_path)

        print(f"Extracting historical score scan page {tgt['pdf_page_index']} from PDF...")
        extract_scan_page_from_pdf(pdf_path, tgt["pdf_page_index"], scan_png_path, dpi=300)

        # Measure count
        from russian_piano_composer.corpus.rc013_event_graph import (
            extract_event_graph_from_musicxml,
        )
        eg = extract_event_graph_from_musicxml(xml_path, score_id=score_id)

        entry = {
            "artifact_id": score_id,
            "composer": tgt["composer"],
            "work": tgt["work"],
            "score_type": "piano_solo",
            "measures_total": eg.total_measures,
            "ground_truth_path": xml_path.replace("\\", "/"),
            "ground_truth_sha256": compute_file_sha256(xml_path),
            "image_path": scan_png_path.replace("\\", "/"),
            "image_sha256": compute_file_sha256(scan_png_path),
            "historical_pdf_path": pdf_path.replace("\\", "/"),
            "historical_pdf_sha256": compute_file_sha256(pdf_path),
            "split": tgt["split"],
            "provenance_class": "REAL_HISTORICAL_SCAN",
            "dataset_name": tgt["dataset_name"],
            "upstream_mscx_url": tgt["mscx_url"],
            "upstream_pdf_url": tgt["pdf_url"],
            "license": tgt["license"],
        }
        v3_registry.append(entry)
        print(f"  Added {score_id}: {eg.total_measures} measures | scan SHA: {entry['image_sha256'][:12]}")

    reg_path = "data/calibration/rc013_machine_validation/rc013_calibration_v3_registry.json"
    with open(reg_path, "w", encoding="utf-8") as f:
        json.dump(v3_registry, f, indent=2)
        f.write("\n")

    print(f"\nSuccessfully created Protocol V3 Calibration Registry: {reg_path} ({len(v3_registry)} items)")


if __name__ == "__main__":
    main()

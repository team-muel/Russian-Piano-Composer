"""Builder for Protocol V5 Candidate-Conditioned Calibration Corpus.

Includes:
- Synthetic controlled baselines (Chopin Op. 28 No. 7, Chopin Op. 28 No. 20, Bach BWV 846)
- Historical threshold calibration split (Chopin Mazurkas Op. 6 No. 1, Op. 7 No. 1, Op. 17 No. 1, Grieg Op. 12 No. 1)
- New untouched final holdout split: Robert Schumann - Kinderszenen Op. 15 No. 1 (Von fremden Ländern und Menschen, Clara Schumann Complete Edition 1879, 22 mm., Peters scan).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import urllib.request
from typing import Any

import pypdfium2 as pdfium


def compute_file_sha256(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


CALIB_V5_DIR = "data/calibration/rc013_machine_validation"
SCORES_DIR = os.path.join(CALIB_V5_DIR, "scores")
HISTORICAL_SCANS_DIR = os.path.join(CALIB_V5_DIR, "historical_scans")
PDFS_DIR = os.path.join(CALIB_V5_DIR, "historical_pdfs")


def download_file_with_retry(url: str, dest_path: str, max_retries: int = 3) -> None:
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as out_f:
                shutil.copyfileobj(resp, out_f)
            return
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Failed to download {url} -> {dest_path}: {e}") from e


def extract_scan_pages_from_pdf(pdf_path: str, page_indices: list[int], output_prefix: str) -> list[str]:
    os.makedirs(os.path.dirname(output_prefix), exist_ok=True)
    pdf = pdfium.PdfDocument(pdf_path)
    out_paths: list[str] = []
    for idx, p_idx in enumerate(page_indices):
        out_png = f"{output_prefix}_p{idx + 1}.png"
        if not os.path.exists(out_png) or os.path.getsize(out_png) == 0:
            page = pdf.get_page(p_idx)
            pil_img = page.render(scale=300 / 72).to_pil()
            pil_img.save(out_png, "PNG")
        out_paths.append(out_png)
    return out_paths


V5_CALIBRATION_TARGETS = [
    # 1. Synthetic Controlled Baselines
    {
        "artifact_id": "chopin_op28_no07",
        "composer": "Frédéric Chopin",
        "work": "Prélude in A major, Op. 28 No. 7",
        "score_type": "piano_solo",
        "measures_total": 16,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/chopin_op28_no07.musicxml",
        "historical_page_indices": [0],
        "historical_printed_pages": ["1"],
        "movement_page_count": 1,
        "historical_page_image_paths": ["data/calibration/rc013_machine_validation/scans/chopin_op28_no07_p1.png"],
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
        "historical_page_indices": [0],
        "historical_printed_pages": ["1"],
        "movement_page_count": 1,
        "historical_page_image_paths": ["data/calibration/rc013_machine_validation/scans/chopin_op28_no20_p1.png"],
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
        "historical_page_indices": [0],
        "historical_printed_pages": ["1"],
        "movement_page_count": 1,
        "historical_page_image_paths": ["data/calibration/rc013_machine_validation/scans/bach_bwv846_prelude_p1.png"],
        "split": "SYNTHETIC_CONTROLLED_CALIBRATION",
        "provenance_class": "SYNTHETIC_DEGRADED_RENDER",
        "dataset_name": "In-Repository Controlled Synthetic Benchmark",
        "digital_dataset_license": "PUBLIC_DOMAIN",
        "historical_scan_status": "SYNTHETIC_VECTOR_RENDER",
    },

    # 2. Real-Scan Historical Calibration Split
    {
        "artifact_id": "chopin_mazurka_op06_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in F-sharp minor, Op. 6 No. 1",
        "score_type": "piano_solo",
        "measures_total": 75,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/chopin_mazurka_op06_no01.musicxml",
        "historical_pdf_path": "data/calibration/rc013_machine_validation/historical_pdfs/chopin_mazurka_op06_no01_source.pdf",
        "historical_pdf_page_indices": [0, 1, 2],
        "historical_printed_pages": ["3", "4", "5"],
        "movement_page_count": 3,
        "historical_page_image_paths": [
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op06_no01_p1.png",
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op06_no01_p2.png",
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op06_no01_p3.png",
        ],
        "first_source_measure": 1,
        "last_source_measure": 75,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 75,
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "dataset_version": "main",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Joseffy edition 1915)",
        "upstream_mscx_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/MS3/BI60-1op06-1.mscx",
        "upstream_pdf_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/pdf/IMSLP111835-PMLP02286-FChopin_Mazurkas%2C_Op.6_Joseffy.pdf",
    },
    {
        "artifact_id": "chopin_mazurka_op07_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in B-flat major, Op. 7 No. 1",
        "score_type": "piano_solo",
        "measures_total": 67,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/chopin_mazurka_op07_no01.musicxml",
        "historical_pdf_path": "data/calibration/rc013_machine_validation/historical_pdfs/chopin_mazurka_op07_no01_source.pdf",
        "historical_pdf_page_indices": [0, 1],
        "historical_printed_pages": ["12", "13"],
        "movement_page_count": 2,
        "historical_page_image_paths": [
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op07_no01_p1.png",
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op07_no01_p2.png",
        ],
        "first_source_measure": 1,
        "last_source_measure": 67,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 67,
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "dataset_version": "main",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Joseffy edition 1915)",
        "upstream_mscx_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/MS3/BI61-1op07-1.mscx",
        "upstream_pdf_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/pdf/IMSLP111837-PMLP02289-FChopin_Mazurkas%2C_Op.7_Joseffy.pdf",
    },
    {
        "artifact_id": "chopin_mazurka_op17_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in B-flat major, Op. 17 No. 1",
        "score_type": "piano_solo",
        "measures_total": 61,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/chopin_mazurka_op17_no01.musicxml",
        "historical_pdf_path": "data/calibration/rc013_machine_validation/historical_pdfs/chopin_mazurka_op17_no01_source.pdf",
        "historical_pdf_page_indices": [0, 1],
        "historical_printed_pages": ["22", "23"],
        "movement_page_count": 2,
        "historical_page_image_paths": [
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op17_no01_p1.png",
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op17_no01_p2.png",
        ],
        "first_source_measure": 1,
        "last_source_measure": 61,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 61,
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "dataset_version": "main",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Joseffy edition 1915)",
        "upstream_mscx_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/MS3/BI77-1op17-1.mscx",
        "upstream_pdf_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/pdf/IMSLP111838-PMLP02281-FChopin_Mazurkas%2C_Op.17_Joseffy.pdf",
    },
    {
        "artifact_id": "grieg_lyric_pieces_op12_no01",
        "composer": "Edvard Grieg",
        "work": "Arietta, Lyric Pieces Op. 12 No. 1",
        "score_type": "piano_solo",
        "measures_total": 23,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/grieg_lyric_pieces_op12_no01.musicxml",
        "historical_pdf_path": "data/calibration/rc013_machine_validation/historical_pdfs/grieg_lyric_pieces_op12_source.pdf",
        "historical_pdf_page_indices": [0],
        "historical_printed_pages": ["1"],
        "movement_page_count": 1,
        "historical_page_image_paths": [
            "data/calibration/rc013_machine_validation/historical_scans/grieg_lyric_pieces_op12_no01_p1.png"
        ],
        "first_source_measure": 1,
        "last_source_measure": 23,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 23,
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
        "dataset_name": "DCMLab/grieg_lyric_pieces",
        "dataset_version": "main",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (C. F. Peters Gesamtausgabe)",
        "upstream_mscx_url": "https://raw.githubusercontent.com/DCMLab/grieg_lyric_pieces/main/MS3/op12n01.mscx",
        "upstream_pdf_url": "https://raw.githubusercontent.com/DCMLab/grieg_lyric_pieces/main/pdf/GA%20Bd.%201%2C%20Heft%20I%20op.%2012.pdf",
    },

    # 3. New Untouched Final Holdout Split (Schumann Op. 15 No. 1)
    {
        "artifact_id": "schumann_kinderszenen_op15_no01",
        "composer": "Robert Schumann",
        "work": "Von fremden Ländern und Menschen, Kinderszenen Op. 15 No. 1",
        "score_type": "piano_solo",
        "measures_total": 22,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/schumann_kinderszenen_op15_no01.musicxml",
        "historical_pdf_path": "data/calibration/rc013_machine_validation/historical_pdfs/schumann_kinderszenen_op15_source.pdf",
        "historical_pdf_page_indices": [1],
        "historical_printed_pages": ["1"],
        "movement_page_count": 1,
        "historical_page_image_paths": [
            "data/calibration/rc013_machine_validation/historical_scans/schumann_kinderszenen_op15_no01_p1.png"
        ],
        "first_source_measure": 1,
        "last_source_measure": 22,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 22,
        "split": "CALIBRATION_V5_FINAL_HOLDOUT",
        "provenance_class": "REAL_HISTORICAL_SCAN",
        "dataset_name": "DCMLab/schumann_kinderszenen",
        "dataset_version": "main",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Clara Schumann Complete Edition, Breitkopf & Härtel 1879)",
        "upstream_mscx_url": "https://raw.githubusercontent.com/DCMLab/schumann_kinderszenen/main/MS3/op15_01.mscx",
        "upstream_pdf_url": "https://raw.githubusercontent.com/DCMLab/schumann_kinderszenen/main/pdf/Kinderszenen_Op_15_Clara_Schumann.pdf",
    },
]


def build_v5_registry() -> list[dict[str, Any]]:
    registry: list[dict[str, Any]] = []

    for tgt in V5_CALIBRATION_TARGETS:
        score_id = tgt["artifact_id"]
        xml_path = tgt["ground_truth_path"].replace("\\", "/")
        img_paths = [p.replace("\\", "/") for p in tgt["historical_page_image_paths"]]

        entry: dict[str, Any] = {
            "artifact_id": score_id,
            "composer": tgt["composer"],
            "work": tgt["work"],
            "score_type": tgt["score_type"],
            "measures_total": tgt["measures_total"],
            "ground_truth_path": xml_path,
            "ground_truth_sha256": compute_file_sha256(xml_path),
            "historical_page_indices": tgt.get("historical_page_indices", [0]),
            "historical_printed_pages": tgt.get("historical_printed_pages", ["1"]),
            "movement_page_count": tgt["movement_page_count"],
            "historical_page_image_paths": img_paths,
            "historical_page_image_sha256s": [compute_file_sha256(p) for p in img_paths],
            "split": tgt["split"],
            "provenance_class": tgt["provenance_class"],
            "dataset_name": tgt["dataset_name"],
            "digital_dataset_license": tgt["digital_dataset_license"],
            "historical_scan_status": tgt["historical_scan_status"],
        }

        if "historical_pdf_path" in tgt:
            pdf_p = tgt["historical_pdf_path"].replace("\\", "/")
            entry["historical_pdf_path"] = pdf_p
            entry["historical_pdf_sha256"] = compute_file_sha256(pdf_p)
            entry["historical_pdf_page_indices"] = tgt["historical_pdf_page_indices"]
            entry["first_source_measure"] = tgt["first_source_measure"]
            entry["last_source_measure"] = tgt["last_source_measure"]
            entry["first_ground_truth_measure"] = tgt["first_ground_truth_measure"]
            entry["last_ground_truth_measure"] = tgt["last_ground_truth_measure"]
            entry["upstream_mscx_url"] = tgt.get("upstream_mscx_url", "")
            entry["upstream_pdf_url"] = tgt.get("upstream_pdf_url", "")

        registry.append(entry)

    registry_path = os.path.join(CALIB_V5_DIR, "rc013_calibration_v5_registry.json")
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
        f.write("\n")

    print(f"Protocol V5 Calibration Registry created at: {registry_path}")
    print(f"Total entries: {len(registry)}")
    return registry


if __name__ == "__main__":
    build_v5_registry()

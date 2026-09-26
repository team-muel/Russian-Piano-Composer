"""Builder for Protocol V6 Genuine Differential Counterfactual Calibration Corpus.

Includes:
- Synthetic controlled baselines (Chopin Op. 28 No. 7, Chopin Op. 28 No. 20, Bach BWV 846)
- Historical threshold calibration split (Chopin Mazurkas Op. 6 No. 1, Op. 7 No. 1, Op. 17 No. 1, Grieg Op. 12 No. 1, Schumann Op. 15 No. 1)
- New untouched final holdout split: Antonín Dvořák - Silhouettes Op. 8 No. 1 (Allegro feroce, 54 mm., Complete Edition / Supraphon, IMSLP59514).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
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


CALIB_V6_DIR = "data/calibration/rc013_machine_validation"
SCORES_DIR = os.path.join(CALIB_V6_DIR, "scores")
HISTORICAL_SCANS_DIR = os.path.join(CALIB_V6_DIR, "historical_scans")
PDFS_DIR = os.path.join(CALIB_V6_DIR, "historical_pdfs")


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


V6_CALIBRATION_TARGETS: list[dict[str, Any]] = [
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
    # 2. Real Historical Scans for Threshold Calibration
    {
        "artifact_id": "chopin_mazurka_op06_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in F-sharp minor, Op. 6 No. 1",
        "score_type": "piano_solo",
        "measures_total": 75,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/chopin_mazurka_op06_no01.musicxml",
        "historical_page_indices": [0],
        "historical_printed_pages": ["3", "4", "5"],
        "movement_page_count": 3,
        "historical_page_image_paths": [
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op06_no01_p1.png",
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op06_no01_p2.png",
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op06_no01_p3.png",
        ],
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Rafael Joseffy Edition, G. Schirmer 1915)",
        "historical_pdf_path": "data/calibration/rc013_machine_validation/historical_pdfs/chopin_mazurka_op06_no01_source.pdf",
        "historical_pdf_page_indices": [0, 1, 2],
        "first_source_measure": 1,
        "last_source_measure": 75,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 75,
        "upstream_mscx_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/MS3/BI60-1op6-1.mscx",
        "upstream_pdf_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/pdf/IMSLP111836-PMLP02279-FChopin_Mazurkas%2C_Op.6_Joseffy.pdf",
    },
    {
        "artifact_id": "chopin_mazurka_op07_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in B-flat major, Op. 7 No. 1",
        "score_type": "piano_solo",
        "measures_total": 64,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/chopin_mazurka_op07_no01.musicxml",
        "historical_page_indices": [0],
        "historical_printed_pages": ["8", "9"],
        "movement_page_count": 2,
        "historical_page_image_paths": [
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op07_no01_p1.png",
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op07_no01_p2.png",
        ],
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Rafael Joseffy Edition, G. Schirmer 1915)",
        "historical_pdf_path": "data/calibration/rc013_machine_validation/historical_pdfs/chopin_mazurka_op07_no01_source.pdf",
        "historical_pdf_page_indices": [0, 1],
        "first_source_measure": 1,
        "last_source_measure": 64,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 64,
        "upstream_mscx_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/MS3/BI61-1op7-1.mscx",
        "upstream_pdf_url": "https://raw.githubusercontent.com/DCMLab/chopin_mazurkas/main/pdf/IMSLP111837-PMLP02280-FChopin_Mazurkas%2C_Op.7_Joseffy.pdf",
    },
    {
        "artifact_id": "chopin_mazurka_op17_no01",
        "composer": "Frédéric Chopin",
        "work": "Mazurka in B-flat major, Op. 17 No. 1",
        "score_type": "piano_solo",
        "measures_total": 61,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/chopin_mazurka_op17_no01.musicxml",
        "historical_page_indices": [0],
        "historical_printed_pages": ["14", "15"],
        "movement_page_count": 2,
        "historical_page_image_paths": [
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op17_no01_p1.png",
            "data/calibration/rc013_machine_validation/historical_scans/chopin_mazurka_op17_no01_p2.png",
        ],
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
        "dataset_name": "DCMLab/chopin_mazurkas",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Rafael Joseffy Edition, G. Schirmer 1915)",
        "historical_pdf_path": "data/calibration/rc013_machine_validation/historical_pdfs/chopin_mazurka_op17_no01_source.pdf",
        "historical_pdf_page_indices": [0, 1],
        "first_source_measure": 1,
        "last_source_measure": 61,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 61,
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
        "historical_page_indices": [0],
        "historical_printed_pages": ["1"],
        "movement_page_count": 1,
        "historical_page_image_paths": ["data/calibration/rc013_machine_validation/historical_scans/grieg_lyric_pieces_op12_no01_p1.png"],
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
        "dataset_name": "DCMLab/grieg_lyric_pieces",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (C. F. Peters Gesamtausgabe)",
        "historical_pdf_path": "data/calibration/rc013_machine_validation/historical_pdfs/grieg_lyric_pieces_op12_source.pdf",
        "historical_pdf_page_indices": [0],
        "first_source_measure": 1,
        "last_source_measure": 23,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 23,
        "upstream_mscx_url": "https://raw.githubusercontent.com/DCMLab/grieg_lyric_pieces/main/MS3/op12n01.mscx",
        "upstream_pdf_url": "https://raw.githubusercontent.com/DCMLab/grieg_lyric_pieces/main/pdf/GA%20Bd.%201%2C%20Heft%20I%20op.%2012.pdf",
    },
    {
        "artifact_id": "schumann_kinderszenen_op15_no01",
        "composer": "Robert Schumann",
        "work": "Von fremden Ländern und Menschen, Kinderszenen Op. 15 No. 1",
        "score_type": "piano_solo",
        "measures_total": 22,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/schumann_kinderszenen_op15_no01.musicxml",
        "historical_page_indices": [0],
        "historical_printed_pages": ["1"],
        "movement_page_count": 1,
        "historical_page_image_paths": ["data/calibration/rc013_machine_validation/historical_scans/schumann_kinderszenen_op15_no01_p1.png"],
        "split": "REAL_SCAN_THRESHOLD_CALIBRATION",
        "provenance_class": "REAL_HISTORICAL_SCAN",
        "dataset_name": "DCMLab/schumann_kinderszenen",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Clara Schumann Complete Edition, Breitkopf & Härtel 1879)",
        "historical_pdf_path": "data/calibration/rc013_machine_validation/historical_pdfs/schumann_kinderszenen_op15_source.pdf",
        "historical_pdf_page_indices": [1],
        "first_source_measure": 1,
        "last_source_measure": 22,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 22,
        "upstream_mscx_url": "https://raw.githubusercontent.com/DCMLab/schumann_kinderszenen/main/MS3/op15_01.mscx",
        "upstream_pdf_url": "https://raw.githubusercontent.com/DCMLab/schumann_kinderszenen/main/pdf/Kinderszenen_Op_15_Clara_Schumann.pdf",
    },
    # 3. New Untouched Final Holdout Split (Dvořák Op. 8 No. 1)
    {
        "artifact_id": "dvorak_silhouettes_op08_no01",
        "composer": "Antonín Dvořák",
        "work": "Allegro feroce, Silhouettes Op. 8 No. 1",
        "score_type": "piano_solo",
        "measures_total": 54,
        "ground_truth_path": "data/calibration/rc013_machine_validation/scores/dvorak_silhouettes_op08_no01.musicxml",
        "historical_page_indices": [0, 1],
        "historical_printed_pages": ["2", "3"],
        "movement_page_count": 2,
        "historical_page_image_paths": [
            "data/calibration/rc013_machine_validation/historical_scans/dvorak_silhouettes_op08_no01_p1.png",
            "data/calibration/rc013_machine_validation/historical_scans/dvorak_silhouettes_op08_no01_p2.png",
        ],
        "split": "CALIBRATION_V6_FINAL_HOLDOUT",
        "provenance_class": "REAL_HISTORICAL_SCAN",
        "dataset_name": "DCMLab/dvorak_silhouettes",
        "digital_dataset_license": "CC BY-NC-SA 4.0",
        "historical_scan_status": "PUBLIC_DOMAIN (Souborné vydání díla Antonína Dvořáka / Supraphon, IMSLP59514)",
        "historical_pdf_path": "data/calibration/rc013_machine_validation/historical_pdfs/dvorak_silhouettes_op08_source.pdf",
        "historical_pdf_page_indices": [1, 2],
        "first_source_measure": 1,
        "last_source_measure": 54,
        "first_ground_truth_measure": 1,
        "last_ground_truth_measure": 54,
        "upstream_mscx_url": "https://raw.githubusercontent.com/DCMLab/dvorak_silhouettes/main/MS3/op08n01.mscx",
        "upstream_pdf_url": "https://raw.githubusercontent.com/DCMLab/dvorak_silhouettes/main/pdf/IMSLP59514-PMLP22823-Dvorak_op.008_Silhouetten_EdSupr_vol1.pdf",
    },
]


def build_rc013_v6_calibration_corpus() -> str:
    """Builds and verifies the full Protocol V6 calibration corpus."""
    os.makedirs(SCORES_DIR, exist_ok=True)
    os.makedirs(HISTORICAL_SCANS_DIR, exist_ok=True)
    os.makedirs(PDFS_DIR, exist_ok=True)

    enriched_targets: list[dict[str, Any]] = []
    mscore_exe = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"

    for entry in V6_CALIBRATION_TARGETS:
        t = dict(entry)
        s_id = t["artifact_id"]

        # 1. Acquire PDF if present
        if "upstream_pdf_url" in t and "historical_pdf_path" in t:
            pdf_p = t["historical_pdf_path"]
            download_file_with_retry(t["upstream_pdf_url"], pdf_p)
            t["historical_pdf_sha256"] = compute_file_sha256(pdf_p)

            # Extract scan pages if needed
            p_indices = t.get("historical_pdf_page_indices", [0])
            out_prefix = os.path.join(HISTORICAL_SCANS_DIR, s_id)
            img_paths = extract_scan_pages_from_pdf(pdf_p, p_indices, out_prefix)
            t["historical_page_image_paths"] = img_paths

        # 2. Acquire Ground-Truth MusicXML
        xml_p = t["ground_truth_path"]
        if (not os.path.exists(xml_p) or os.path.getsize(xml_p) == 0) and "upstream_mscx_url" in t:
            mscx_p = os.path.join(SCORES_DIR, f"{s_id}.mscx")
            download_file_with_retry(t["upstream_mscx_url"], mscx_p)
            if os.path.exists(mscore_exe):
                subprocess.run([mscore_exe, "-o", xml_p, mscx_p], check=True, capture_output=True)

        if os.path.exists(xml_p):
            t["ground_truth_sha256"] = compute_file_sha256(xml_p)

        # 3. Hash image paths
        img_shas: list[str] = []
        for img_p in t.get("historical_page_image_paths", []):
            if os.path.exists(img_p):
                img_shas.append(compute_file_sha256(img_p))
        t["historical_page_image_sha256s"] = img_shas

        enriched_targets.append(t)

    registry_path = os.path.join(CALIB_V6_DIR, "rc013_calibration_v6_registry.json")
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(enriched_targets, f, indent=2)

    print(f"Protocol V6 Calibration Registry created at: {registry_path}")
    print(f"Total entries: {len(enriched_targets)}")
    return registry_path


if __name__ == "__main__":
    build_rc013_v6_calibration_corpus()

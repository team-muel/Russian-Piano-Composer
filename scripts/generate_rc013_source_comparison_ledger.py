"""Generates per-measure source comparison ledger records for all 9 RC-013 pilot scores.

Each score gets a <score>.source_comparison.json file containing one record per measure,
with all required schema fields populated with their initial values.

comparison_method = PENDING_HUMAN_REVIEW for all records:
  A human reviewer must examine each measure against the printed source scan
  and update: pitch_status, duration_status, rest_status, staff_status,
  voice_status, tie_status, tuplet_status, grace_status, key_signature_status,
  time_signature_status, ornament_status, repeat_status, errors_found,
  corrections_applied, unresolved_ambiguity, and set comparison_method accordingly.

A score may only become SOURCE_FIDELITY_VERIFIED when:
  1. 100% of measures have comparison records with comparison_method != PENDING_HUMAN_REVIEW
  2. All critical discrepancies corrected (remaining_critical_discrepancies == 0)
  3. unresolved_critical_ambiguities == 0
  4. symbolic_file_sha256 frozen after corrections
This script does NOT grant SOURCE_FIDELITY_VERIFIED status.
"""

from __future__ import annotations

import hashlib
import json
import os
import xml.etree.ElementTree as ET
from datetime import UTC, datetime

import pandas as pd

# Score measure counts (from validated MusicXML files)
SCORE_MEASURE_COUNTS: dict[str, int] = {
    "sergei_lyapunov_op11_no01": 32,
    "sergei_lyapunov_op11_no02": 24,
    "sergei_lyapunov_op11_no03": 24,
    "anton_arensky_op36_no01": 24,
    "anton_arensky_op36_no02": 24,
    "anton_arensky_op36_no13": 24,
    "anatoly_lyadov_op40_no02": 24,
    "anatoly_lyadov_op40_no03": 24,
    "anatoly_lyadov_op46_no04": 24,
}

# Source page mappings: printed page ranges from rc013_source_candidates.csv
# Format: (pdf_page_index_start_0based, printed_page_start, total_pdf_pages)
SOURCE_PAGE_INFO: dict[str, dict] = {
    "sergei_lyapunov_op11_no01": {
        "source_file_name": "Lyapunov_-_Etudes,_Op.11.pdf",
        "source_file_sha256": "1083b34ad2e8a972877d8f3da7458d265976ced42377ad33efe14ad11157beb0",
        "pdf_page_index_start": 0,   # 0-based index of first page of this work
        "printed_page_start": 1,      # printed page number on score
        "total_pdf_pages": 30,
        "work_page_range": "1-8",     # printed pages (from CSV)
    },
    "sergei_lyapunov_op11_no02": {
        "source_file_name": "Lyapunov_-_Etudes,_Op.11.pdf",
        "source_file_sha256": "1083b34ad2e8a972877d8f3da7458d265976ced42377ad33efe14ad11157beb0",
        "pdf_page_index_start": 8,
        "printed_page_start": 9,
        "total_pdf_pages": 30,
        "work_page_range": "9-20",
    },
    "sergei_lyapunov_op11_no03": {
        "source_file_name": "Lyapunov_-_Etudes,_Op.11.pdf",
        "source_file_sha256": "1083b34ad2e8a972877d8f3da7458d265976ced42377ad33efe14ad11157beb0",
        "pdf_page_index_start": 20,
        "printed_page_start": 21,
        "total_pdf_pages": 30,
        "work_page_range": "21-30",
    },
    "anton_arensky_op36_no01": {
        "source_file_name": "Arensky_morceaux_op36-1.pdf",
        "source_file_sha256": "d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855",
        "pdf_page_index_start": 0,
        "printed_page_start": 1,
        "total_pdf_pages": 27,
        "work_page_range": "1-4",
    },
    "anton_arensky_op36_no02": {
        "source_file_name": "Arensky_morceaux_op36-1.pdf",
        "source_file_sha256": "d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855",
        "pdf_page_index_start": 4,
        "printed_page_start": 5,
        "total_pdf_pages": 27,
        "work_page_range": "5-12",
    },
    "anton_arensky_op36_no13": {
        "source_file_name": "Arensky_Morceaux_op.36_No.13-18.pdf",
        "source_file_sha256": "eaf21776599c1069a78cce881a518a40badb604b9061d4ff6d60537dcb3b87f5",
        "pdf_page_index_start": 0,
        "printed_page_start": 1,
        "total_pdf_pages": 39,
        "work_page_range": "1-5",
    },
    "anatoly_lyadov_op40_no02": {
        "source_file_name": "31761108768078.pdf",
        "source_file_sha256": "8484f2d6e88df70001935921964ed6c805f3df069d02cd4d0cd466d8f6cdc8f5",
        "pdf_page_index_start": 0,
        "printed_page_start": 1,
        "total_pdf_pages": None,  # Could not extract from trailer — needs full PDF parse
        "work_page_range": "1-3",
    },
    "anatoly_lyadov_op40_no03": {
        "source_file_name": "31761108768078.pdf",
        "source_file_sha256": "8484f2d6e88df70001935921964ed6c805f3df069d02cd4d0cd466d8f6cdc8f5",
        "pdf_page_index_start": 3,
        "printed_page_start": 4,
        "total_pdf_pages": None,
        "work_page_range": "4-6",
    },
    "anatoly_lyadov_op46_no04": {
        "source_file_name": "31761108768078.pdf",
        "source_file_sha256": "8484f2d6e88df70001935921964ed6c805f3df069d02cd4d0cd466d8f6cdc8f5",
        "pdf_page_index_start": 6,
        "printed_page_start": 7,
        "total_pdf_pages": None,
        "work_page_range": "7-9",
    },
}

# Allowed comparison_method values (final states after human review)
ALLOWED_COMPARISON_METHODS = {
    "PENDING_HUMAN_REVIEW",    # Not yet compared
    "HUMAN_MEASURE_COMPARISON",  # Human compared measure against printed source
    "HUMAN_NOTE_BY_NOTE",       # Human verified each note individually
}

# Allowed status values for element-level checks
ALLOWED_ELEMENT_STATUSES = {
    "NOT_REVIEWED",      # Initial state; comparison not performed
    "MATCH",             # Matches source exactly
    "CORRECTED",         # Discrepancy found and corrected
    "DISCREPANCY",       # Discrepancy found, not yet corrected
    "NOT_APPLICABLE",    # Element type not present in this measure
    "AMBIGUOUS",         # Source is ambiguous, requires decision
}


def compute_sha256_file(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_measure_count_from_musicxml(file_path: str) -> int:
    """Parse MusicXML to count measures in the first part."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Handle namespace
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"
    part = root.find(f"{ns}part")
    if part is None:
        return 0
    return len(list(part.findall(f"{ns}measure")))


def make_pending_measure_record(
    canonical_work_id: str,
    source_info: dict,
    symbolic_sha: str,
    measure_number: int,
    source_pdf_page_index: int,
    printed_page_number: int,
    work_local_page: int,
) -> dict:
    """Create a single PENDING_HUMAN_REVIEW measure comparison record."""
    return {
        "canonical_work_id": canonical_work_id,
        "source_file_sha256": source_info["source_file_sha256"],
        "symbolic_file_sha256": symbolic_sha,
        "source_pdf_page_index": source_pdf_page_index,   # 0-based index in PDF file
        "printed_page_number": printed_page_number,        # Number printed on the score page
        "work_local_page": work_local_page,                # 1-based page within this work
        "measure_number": measure_number,
        # --- Comparison provenance (set by reviewer, not automated) ---
        "comparison_method": "PENDING_HUMAN_REVIEW",
        "reviewer_type": None,
        "reviewer_identifier": None,
        "review_timestamp": None,
        # --- Element-level fidelity statuses (PENDING until human comparison) ---
        "pitch_status": "NOT_REVIEWED",
        "duration_status": "NOT_REVIEWED",
        "rest_status": "NOT_REVIEWED",
        "staff_status": "NOT_REVIEWED",
        "voice_status": "NOT_REVIEWED",
        "tie_status": "NOT_REVIEWED",
        "tuplet_status": "NOT_REVIEWED",
        "grace_status": "NOT_REVIEWED",
        "key_signature_status": "NOT_REVIEWED",
        "time_signature_status": "NOT_REVIEWED",
        "ornament_status": "NOT_REVIEWED",
        "repeat_status": "NOT_REVIEWED",
        # --- Error and ambiguity tracking ---
        "errors_found": [],            # List of {error_type, before, after, source_page}
        "corrections_applied": [],     # List of {error_type, before, after}
        "unresolved_ambiguity": False,
        "unresolved_ambiguity_description": None,
        "ambiguity_severity": None,    # "CRITICAL" | "NONCRITICAL" | null
    }


def estimate_page_for_measure(
    measure_number: int,
    total_measures: int,
    page_range_str: str,
) -> tuple[int, int, int]:
    """
    Estimate which source page a measure falls on.
    Returns (pdf_page_index_0based, printed_page_number, work_local_page).
    This is a STRUCTURAL ESTIMATE for the ledger scaffold;
    the actual page must be confirmed by a human reviewer.
    """
    parts = page_range_str.split("-")
    page_start = int(parts[0])
    page_end = int(parts[1])
    num_pages = page_end - page_start + 1

    # Distribute measures evenly across pages (structural estimate only)
    if total_measures > 0:
        # 0-based page within work (0 = first page of work)
        local_page_0 = min(
            int((measure_number - 1) * num_pages / total_measures),
            num_pages - 1,
        )
    else:
        local_page_0 = 0

    work_local_page = local_page_0 + 1            # 1-based
    printed_page_number = page_start + local_page_0
    return printed_page_number, work_local_page


def main() -> None:
    df = pd.read_csv("data/manifests/rc013_source_candidates.csv")
    reviews_dir = "data/reviews/rc013"
    os.makedirs(reviews_dir, exist_ok=True)

    total_records = 0

    for _, row in df.iterrows():
        comp = row["composer"]
        opus = row["opus_or_catalogue"]
        mov = int(row["movement"])
        fname_opus = opus.lower().replace(" ", "").replace(".", "")
        comp_slug = comp.lower().replace(" ", "_")
        score_id = f"{comp_slug}_{fname_opus}_no{mov:02d}"
        canonical_work_id = f"{comp_slug}_{fname_opus}_m{mov:02d}"

        score_file = f"data/scores/rc013/canonical/{score_id}.musicxml"
        if not os.path.exists(score_file):
            print(f"SKIP (not found): {score_file}")
            continue

        source_info = SOURCE_PAGE_INFO.get(score_id)
        if source_info is None:
            print(f"SKIP (no page info): {score_id}")
            continue

        symbolic_sha = compute_sha256_file(score_file)
        num_measures = get_measure_count_from_musicxml(score_file)
        page_range = row["page_range"]
        pdf_page_base = source_info["pdf_page_index_start"]

        measure_records = []
        for m_num in range(1, num_measures + 1):
            printed_page, work_local_page = estimate_page_for_measure(
                m_num, num_measures, page_range
            )
            # pdf_page_index is 0-based; printed_page is already from the work's
            # range, so we add the 0-based pdf offset to get the absolute pdf page
            pdf_page_index = pdf_page_base + (printed_page - int(page_range.split("-")[0]))

            record = make_pending_measure_record(
                canonical_work_id=canonical_work_id,
                source_info=source_info,
                symbolic_sha=symbolic_sha,
                measure_number=m_num,
                source_pdf_page_index=pdf_page_index,
                printed_page_number=printed_page,
                work_local_page=work_local_page,
            )
            measure_records.append(record)

        ledger = {
            "schema_version": "rc013_source_comparison_v1",
            "canonical_work_id": canonical_work_id,
            "score_id": score_id,
            "source_file_name": source_info["source_file_name"],
            "source_file_sha256": source_info["source_file_sha256"],
            "symbolic_file_sha256": symbolic_sha,
            "total_measures": num_measures,
            "total_pdf_pages": source_info["total_pdf_pages"],
            "work_page_range_in_pdf": page_range,
            "pdf_page_index_start": pdf_page_base,
            "ledger_generated_at": datetime.now(UTC).isoformat(),
            "ledger_status": "PENDING_HUMAN_REVIEW",
            # --- Acceptance criteria (read-only until human completes all measures) ---
            "acceptance_criteria": {
                "require_all_measures_compared": True,
                "require_zero_critical_discrepancies": True,
                "require_zero_unresolved_critical_ambiguities": True,
                "require_symbolic_sha_frozen_after_corrections": True,
            },
            # --- Per-score summary (to be filled in by reviewer) ---
            "summary": {
                "measures_total": num_measures,
                "measures_compared": 0,
                "initial_discrepancies": None,
                "corrected_discrepancies": None,
                "remaining_critical_discrepancies": None,
                "remaining_noncritical_ambiguities": None,
                "source_fidelity_verdict": "PENDING_SOURCE_COMPARISON",
            },
            "measures": measure_records,
        }

        out_path = os.path.join(reviews_dir, f"{score_id}.source_comparison.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=2, sort_keys=True)

        total_records += num_measures
        print(f"  {score_id}: {num_measures} measure records -> {out_path}")

    print(f"\nGenerated source comparison ledgers for {len(df)} scores ({total_records} measure records).")
    print("All records: comparison_method = PENDING_HUMAN_REVIEW")
    print("             source_fidelity_verdict = PENDING_SOURCE_COMPARISON")
    print("A score may only become SOURCE_FIDELITY_VERIFIED when all acceptance criteria are met.")


if __name__ == "__main__":
    main()

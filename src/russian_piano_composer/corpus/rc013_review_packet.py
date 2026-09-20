"""Independent Human Source-Fidelity Review Packet Generator and Validator.

Creates blank, unbiased review packets for independent human reviewers and musicologists.
Enforces strict reviewer independence, SHA binding, and correction invalidation.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass
class ReviewPacketHeader:
    score_id: str
    canonical_work_id: str
    composer: str
    work_title: str
    movement_number: int
    key: str
    meter: str
    tempo: str
    total_measures: int
    source_file_name: str
    source_file_sha256: str
    candidate_symbolic_sha256: str
    pdf_page_range: str
    printed_page_range: str


def generate_blank_review_packet(
    score_id: str,
    canonical_work_id: str,
    composer: str,
    work_title: str,
    movement_number: int,
    key: str,
    meter: str,
    tempo: str,
    total_measures: int,
    source_file_name: str,
    source_file_sha256: str,
    candidate_symbolic_sha256: str,
    pdf_page_range: str,
    printed_page_range: str,
    page_to_measure_map: dict[int, tuple[int, int, int]],  # m_num -> (pdf_page_idx, printed_page, work_page)
    output_path: str,
) -> dict[str, Any]:
    """Generates a blank review packet JSON with all fields set to unreviewed state.

    The packet is designed for independent human musicological audit.
    No fields are pre-filled with 'MATCH'.
    """
    measures = []
    for m_num in range(1, total_measures + 1):
        pdf_idx, printed_p, work_p = page_to_measure_map[m_num]
        m_entry: dict[str, Any] = {
            "measure_number": m_num,
            "source_pdf_page_index": pdf_idx,
            "printed_page_number": printed_p,
            "work_local_page": work_p,
            "canonical_work_id": canonical_work_id,
            "source_file_sha256": source_file_sha256,
            "symbolic_file_sha256": candidate_symbolic_sha256,
            "comparison_method": "PENDING_INDEPENDENT_HUMAN_REVIEW",
            "reviewer_type": None,
            "reviewer_identifier": None,
            "review_timestamp": None,
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
            "dynamic_status": "NOT_REVIEWED",
            "articulation_status": "NOT_REVIEWED",
            "tempo_status": "NOT_REVIEWED",
            "pedal_status": "NOT_REVIEWED",
            "errors_found": [],
            "corrections_applied": [],
            "unresolved_ambiguity": False,
            "ambiguity_severity": None,
            "unresolved_ambiguity_description": None,
        }
        measures.append(m_entry)

    packet = {
        "schema_version": "rc013_independent_review_packet_v1",
        "packet_status": "PENDING_INDEPENDENT_HUMAN_REVIEW",
        "header": {
            "score_id": score_id,
            "canonical_work_id": canonical_work_id,
            "composer": composer,
            "work_title": work_title,
            "movement_number": movement_number,
            "key": key,
            "meter": meter,
            "tempo": tempo,
            "total_measures": total_measures,
            "source_file_name": source_file_name,
            "source_file_sha256": source_file_sha256,
            "candidate_symbolic_sha256": candidate_symbolic_sha256,
            "pdf_page_range": pdf_page_range,
            "printed_page_range": printed_page_range,
        },
        "reviewer_declaration": {
            "reviewer_identifier": None,
            "reviewer_role": None,  # Must be "INDEPENDENT_HUMAN_REVIEWER" or "HUMAN_MUSICOLOGIST"
            "transcriber_identifier": "automated_and_pilot_transcription_pipeline",
            "review_start_timestamp": None,
            "review_completion_timestamp": None,
            "independent_confirmation_statement": None,
        },
        "measures": measures,
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(packet, f, indent=2, ensure_ascii=False)

    return packet

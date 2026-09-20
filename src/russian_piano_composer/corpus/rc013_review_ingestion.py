"""Deterministic Ingestion and Validation of Genuine Independent Human Review Evidence.

Validates:
- Non-empty, valid human reviewer identity (INDEPENDENT_HUMAN_REVIEWER or HUMAN_MUSICOLOGIST).
- Reviewer independence (reviewer_identifier != transcriber_identifier, non-AI).
- Exact SHA256 cryptographic binding (source PDF SHA and current symbolic MusicXML SHA).
- Full measure sequence completeness (1..total_measures with 0 missing/duplicate).
- All 16 element status dimensions reviewed per measure.
- Stale review invalidation if symbolic MusicXML has changed.
- Zero unresolved critical ambiguities and zero critical discrepancies.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from russian_piano_composer.corpus.rc013_fidelity import (
    VALID_TERMINAL_ELEMENT_STATUSES,
)

DISALLOWED_REVIEWER_TYPES: frozenset[str] = frozenset({
    "PRIMARY_TRANSCRIBER_SOURCE_CHECK",
    "AUTOMATED_QC",
    "AI_REVIEWER",
    "AGENT_REVIEWER",
    "ANTIGRAVITY",
    "MODEL",
})


@dataclass
class ReviewIngestionResult:
    valid: bool
    score_id: str
    status: str
    reviewer_identifier: str | None
    reviewer_role: str | None
    reviewed_symbolic_sha: str | None
    current_symbolic_sha: str | None
    reviewed_source_sha: str | None
    canonical_source_sha: str | None
    total_measures: int
    measures_reviewed: int
    critical_ambiguities_count: int
    errors: list[str] = field(default_factory=list)


def validate_and_ingest_human_review_packet(
    packet_path: str,
    canonical_source_sha: str,
    current_symbolic_sha: str,
    transcriber_identifier: str = "automated_and_pilot_transcription_pipeline",
) -> ReviewIngestionResult:
    """Validates and deterministically ingests completed human review evidence."""
    errors: list[str] = []

    if not os.path.exists(packet_path):
        return ReviewIngestionResult(
            valid=False,
            score_id=os.path.basename(packet_path).replace(".json", ""),
            status="PACKET_FILE_MISSING",
            reviewer_identifier=None,
            reviewer_role=None,
            reviewed_symbolic_sha=None,
            current_symbolic_sha=current_symbolic_sha,
            reviewed_source_sha=None,
            canonical_source_sha=canonical_source_sha,
            total_measures=0,
            measures_reviewed=0,
            critical_ambiguities_count=0,
            errors=[f"Review packet file not found: {packet_path}"],
        )

    with open(packet_path, encoding="utf-8") as f:
        packet: dict[str, Any] = json.load(f)

    header = packet.get("header", {})
    score_id = str(header.get("score_id", ""))
    total_measures = int(header.get("total_measures", 0))
    packet_source_sha = str(header.get("source_file_sha256", ""))
    packet_sym_sha = str(header.get("candidate_symbolic_sha256", ""))

    declaration = packet.get("reviewer_declaration", {})
    r_id = declaration.get("reviewer_identifier")
    r_role = declaration.get("reviewer_role")
    t_id = declaration.get("transcriber_identifier") or transcriber_identifier
    completion_ts = declaration.get("review_completion_timestamp")

    # 1. Reviewer identity and independence checks
    if not r_id or not str(r_id).strip():
        errors.append("EMPTY_REVIEWER_IDENTIFIER: Reviewer identifier is required")
    elif str(r_id).strip().upper() in {"AI", "AGENT", "ANTIGRAVITY", "MODEL", "UNKNOWN", "NONE"}:
        errors.append(f"INVALID_REVIEWER_IDENTIFIER: '{r_id}' cannot be an AI/automated agent")

    if not r_role or r_role not in {"INDEPENDENT_HUMAN_REVIEWER", "HUMAN_MUSICOLOGIST"}:
        errors.append(f"INVALID_REVIEWER_ROLE: '{r_role}' is not an authorized human reviewer role")

    if r_role in DISALLOWED_REVIEWER_TYPES:
        errors.append(f"DISALLOWED_REVIEWER_TYPE: '{r_role}' cannot grant independent source fidelity")

    if r_id and t_id and str(r_id).strip().lower() == str(t_id).strip().lower():
        errors.append(f"SELF_CERTIFICATION_DISALLOWED: Reviewer '{r_id}' matches transcriber '{t_id}'")

    if not completion_ts or not str(completion_ts).strip():
        errors.append("EMPTY_REVIEW_TIMESTAMP: Review completion timestamp is required")

    # 2. Cryptographic SHA binding
    if packet_source_sha != canonical_source_sha:
        errors.append(f"SOURCE_SHA_MISMATCH: Packet has {packet_source_sha}, canonical source is {canonical_source_sha}")

    if packet_sym_sha != current_symbolic_sha:
        errors.append(
            f"STALE_AFTER_SYMBOLIC_CHANGE: Packet reviewed SHA {packet_sym_sha} != current live SHA {current_symbolic_sha}"
        )

    # 3. Measures sequence and completeness
    measures = packet.get("measures", [])
    if len(measures) != total_measures:
        errors.append(f"MEASURE_COUNT_MISMATCH: Expected {total_measures} measures, found {len(measures)}")

    expected_seq = list(range(1, total_measures + 1))
    actual_seq = [m.get("measure_number") for m in measures]
    if actual_seq != expected_seq:
        errors.append(f"MEASURE_SEQUENCE_VIOLATION: Sequence {actual_seq[:5]}... != 1..{total_measures}")

    reviewed_count = 0
    critical_ambiguities = 0

    for idx, m in enumerate(measures, start=1):
        m_num = m.get("measure_number", idx)
        comp_method = m.get("comparison_method")
        if comp_method not in {"HUMAN_MEASURE_COMPARISON", "HUMAN_NOTE_BY_NOTE"}:
            errors.append(f"Measure {m_num}: Incomplete comparison method '{comp_method}'")
        else:
            reviewed_count += 1

        # Check per-dimension review status
        for dim in [
            "pitch_status", "duration_status", "rest_status", "staff_status",
            "voice_status", "tie_status", "tuplet_status", "grace_status",
            "key_signature_status", "time_signature_status", "ornament_status",
            "repeat_status", "dynamic_status", "articulation_status",
            "tempo_status", "pedal_status",
        ]:
            st = m.get(dim)
            if st == "NOT_REVIEWED":
                errors.append(f"Measure {m_num}: Dimension {dim} is NOT_REVIEWED")
            elif st not in VALID_TERMINAL_ELEMENT_STATUSES:
                errors.append(f"Measure {m_num}: Dimension {dim} has invalid status '{st}'")

        if m.get("unresolved_ambiguity") is True and m.get("ambiguity_severity") == "CRITICAL":
            critical_ambiguities += 1
            errors.append(f"Measure {m_num}: Unresolved CRITICAL ambiguity present")

    valid = len(errors) == 0
    if valid:
        status = "SOURCE_FIDELITY_VERIFIED"
    elif any("STALE_AFTER_SYMBOLIC_CHANGE" in e for e in errors):
        status = "STALE_AFTER_SYMBOLIC_CHANGE"
    elif any("EMPTY_REVIEWER_IDENTIFIER" in e or "PENDING" in str(packet.get("packet_status", "")) for e in errors):
        status = "PENDING_INDEPENDENT_HUMAN_REVIEW"
    else:
        status = "REVIEW_VALIDATION_FAILED"

    return ReviewIngestionResult(
        valid=valid,
        score_id=score_id,
        status=status,
        reviewer_identifier=r_id,
        reviewer_role=r_role,
        reviewed_symbolic_sha=packet_sym_sha,
        current_symbolic_sha=current_symbolic_sha,
        reviewed_source_sha=packet_source_sha,
        canonical_source_sha=canonical_source_sha,
        total_measures=total_measures,
        measures_reviewed=reviewed_count,
        critical_ambiguities_count=critical_ambiguities,
        errors=errors,
    )

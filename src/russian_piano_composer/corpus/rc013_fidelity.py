"""RC-013 Source-to-Symbolic Fidelity Verification and Audit Gate Engine.

Enforces fail-closed, cryptographic, measure-by-measure source fidelity gates:
- Validates per-measure source comparison ledgers against frozen source manifests.
- Requires both canonical source SHA authority and current symbolic SHA authority.
- Enforces 100% measure comparison completion.
- Disallows PENDING_HUMAN_REVIEW and unreviewed element fields.
- Validates human reviewer semantics (allowed human reviewer types, non-empty id/timestamp).
- Enforces measure identity integrity (strictly monotonic 1..total_measures, no duplicates/missing/extra).
- Forbids critical discrepancies and unresolved critical ambiguities.
- Cryptographically binds source PDF SHA256 and frozen symbolic MusicXML SHA256.
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, field
from typing import Any

REQUIRED_MEASURE_FIELDS: frozenset[str] = frozenset({
    "canonical_work_id",
    "source_file_sha256",
    "symbolic_file_sha256",
    "source_pdf_page_index",
    "printed_page_number",
    "work_local_page",
    "measure_number",
    "comparison_method",
    "pitch_status",
    "duration_status",
    "rest_status",
    "staff_status",
    "voice_status",
    "tie_status",
    "tuplet_status",
    "grace_status",
    "key_signature_status",
    "time_signature_status",
    "ornament_status",
    "repeat_status",
    "errors_found",
    "corrections_applied",
    "unresolved_ambiguity",
    "reviewer_type",
    "reviewer_identifier",
    "review_timestamp",
})

ELEMENT_STATUS_FIELDS: tuple[str, ...] = (
    "pitch_status",
    "duration_status",
    "rest_status",
    "staff_status",
    "voice_status",
    "tie_status",
    "tuplet_status",
    "grace_status",
    "key_signature_status",
    "time_signature_status",
    "ornament_status",
    "repeat_status",
)

VALID_TERMINAL_ELEMENT_STATUSES: frozenset[str] = frozenset({
    "MATCH",
    "CORRECTED",
    "NOT_APPLICABLE",
    "AMBIGUOUS",
})

ALLOWED_HUMAN_REVIEWER_TYPES: frozenset[str] = frozenset({
    "PRIMARY_TRANSCRIBER_SOURCE_CHECK",
    "HUMAN_MUSICOLOGIST",
    "INDEPENDENT_HUMAN_REVIEWER",
})


class SourceFidelityGateError(Exception):
    """Raised when a source fidelity verification check fails."""


@dataclass
class FidelityValidationResult:
    valid: bool
    score_id: str
    canonical_work_id: str
    total_measures: int
    measures_compared: int
    remaining_critical_discrepancies: int
    unresolved_critical_ambiguities: int
    fidelity_status: str
    error_category: str | None = None
    errors: list[str] = field(default_factory=list)


def compute_sha256_file(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_canonical_source_manifest(manifest_csv_path: str) -> dict[str, str]:
    """Loads canonical mapping from canonical_work_id or score_id to source_file_sha256."""
    mapping: dict[str, str] = {}
    with open(manifest_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            comp = row["composer"].lower().replace(" ", "_")
            opus = row["opus_or_catalogue"].lower().replace(" ", "").replace(".", "")
            mov = int(row["movement"])
            c_work_id = f"{comp}_{opus}_m{mov:02d}"
            score_id = f"{comp}_{opus}_no{mov:02d}"
            sha = str(row["source_file_sha256"]).strip()
            mapping[c_work_id] = sha
            mapping[score_id] = sha
    return mapping


def validate_source_comparison_ledger(
    ledger: dict[str, Any],
    canonical_source_sha: str | None = None,
    current_symbolic_sha: str | None = None,
    manifest_csv_path: str | None = None,
    fail_fast: bool = False,
) -> FidelityValidationResult:
    """Validates a single score's source comparison ledger against all acceptance rules.

    Fail-closed:
      - If canonical source SHA authority is missing or cannot be resolved: FAIL.
      - If current symbolic SHA is missing or empty: FAIL.
      - If any measure or element violates integrity: FAIL.
    """
    errors: list[str] = []
    error_categories: list[str] = []

    score_id = str(ledger.get("score_id", ""))
    c_work_id = str(ledger.get("canonical_work_id", ""))
    total_measures = int(ledger.get("total_measures", 0))
    measures = ledger.get("measures", [])

    if manifest_csv_path and not canonical_source_sha:
        manifest_map = load_canonical_source_manifest(manifest_csv_path)
        canonical_source_sha = manifest_map.get(c_work_id) or manifest_map.get(score_id)

    # 1. Mandatory Authority Verification (Fail-closed)
    if not canonical_source_sha or not canonical_source_sha.strip():
        errors.append("Missing canonical source SHA authority")
        error_categories.append("MISSING_SOURCE_AUTHORITY")

    if not current_symbolic_sha or not current_symbolic_sha.strip():
        errors.append("Missing current symbolic SHA authority")
        error_categories.append("MISSING_SYMBOLIC_AUTHORITY")

    # 2. Source SHA Verification
    ledger_source_sha = ledger.get("source_file_sha256")
    if canonical_source_sha and ledger_source_sha != canonical_source_sha:
        errors.append(
            f"Source SHA mismatch in ledger header: expected {canonical_source_sha}, got {ledger_source_sha}"
        )
        error_categories.append("SOURCE_SHA_MISMATCH")

    # 3. Symbolic SHA Verification
    ledger_symbolic_sha = ledger.get("symbolic_file_sha256")
    if current_symbolic_sha and ledger_symbolic_sha != current_symbolic_sha:
        errors.append(
            f"Symbolic SHA mismatch (file changed after review): expected {current_symbolic_sha}, got {ledger_symbolic_sha}"
        )
        error_categories.append("SYMBOLIC_SHA_MISMATCH")

    # 4. Measures count and sequence integrity (Measure Identity Integrity)
    if total_measures <= 0:
        errors.append(f"Invalid total_measures: {total_measures}")
        error_categories.append("INVALID_MEASURE_COUNT")
    elif len(measures) != total_measures:
        errors.append(
            f"Measure count mismatch: ledger has {len(measures)} measures, declared total_measures={total_measures}"
        )
        error_categories.append("MEASURE_COUNT_MISMATCH")

    measure_numbers = [m.get("measure_number") for m in measures]
    expected_sequence = list(range(1, total_measures + 1)) if total_measures > 0 else []
    if measure_numbers != expected_sequence:
        errors.append(
            f"Measure sequence violation: measure numbers {measure_numbers[:5]}... do not match expected sequence 1..{total_measures}"
        )
        error_categories.append("MEASURE_SEQUENCE_VIOLATION")

    # 5. Per-measure validation
    compared_count = 0
    unresolved_critical_ambiguities = 0

    for idx, m in enumerate(measures, start=1):
        m_num = m.get("measure_number", idx)

        # Check required fields
        m_keys = set(m.keys())
        missing_fields = REQUIRED_MEASURE_FIELDS - m_keys
        if missing_fields:
            errors.append(f"Measure {m_num}: missing required fields: {sorted(missing_fields)}")
            error_categories.append("SCHEMA_FIELD_MISSING")

        # Source & symbolic SHA matching inside measure record
        if canonical_source_sha and m.get("source_file_sha256") != canonical_source_sha:
            errors.append(f"Measure {m_num}: source_file_sha256 mismatch in measure record")
            error_categories.append("SOURCE_SHA_MISMATCH")
        if current_symbolic_sha and m.get("symbolic_file_sha256") != current_symbolic_sha:
            errors.append(f"Measure {m_num}: symbolic_file_sha256 mismatch in measure record")
            error_categories.append("SYMBOLIC_SHA_MISMATCH")

        # Comparison method
        comp_method = m.get("comparison_method")
        if comp_method == "PENDING_HUMAN_REVIEW":
            errors.append(f"Measure {m_num}: comparison_method is PENDING_HUMAN_REVIEW")
            error_categories.append("PENDING_HUMAN_REVIEW")
        elif comp_method in {"HUMAN_MEASURE_COMPARISON", "HUMAN_NOTE_BY_NOTE"}:
            compared_count += 1
            # Human Review Semantics verification
            r_type = m.get("reviewer_type")
            if r_type not in ALLOWED_HUMAN_REVIEWER_TYPES:
                errors.append(
                    f"Measure {m_num}: invalid reviewer_type '{r_type}' for human comparison (must be in {sorted(ALLOWED_HUMAN_REVIEWER_TYPES)})"
                )
                error_categories.append("INVALID_REVIEWER_TYPE")

            r_id = m.get("reviewer_identifier")
            if not r_id or not str(r_id).strip():
                errors.append(f"Measure {m_num}: empty reviewer_identifier")
                error_categories.append("EMPTY_REVIEWER_ID")

            r_ts = m.get("review_timestamp")
            if not r_ts or not str(r_ts).strip():
                errors.append(f"Measure {m_num}: empty review_timestamp")
                error_categories.append("EMPTY_REVIEW_TIMESTAMP")
        else:
            errors.append(f"Measure {m_num}: invalid comparison_method: {comp_method}")
            error_categories.append("INVALID_COMPARISON_METHOD")

        # Element statuses
        for status_key in ELEMENT_STATUS_FIELDS:
            st = m.get(status_key)
            if st == "NOT_REVIEWED":
                errors.append(f"Measure {m_num}: {status_key} is NOT_REVIEWED")
                error_categories.append("UNREVIEWED_ELEMENT")
            elif st == "DISCREPANCY":
                errors.append(f"Measure {m_num}: {status_key} has uncorrected DISCREPANCY")
                error_categories.append("UNCORRECTED_DISCREPANCY")
            elif st not in VALID_TERMINAL_ELEMENT_STATUSES:
                errors.append(f"Measure {m_num}: {status_key} has invalid status {st}")
                error_categories.append("INVALID_ELEMENT_STATUS")

        # Ambiguity check
        if m.get("unresolved_ambiguity") is True:
            sev = m.get("ambiguity_severity")
            if sev == "CRITICAL":
                unresolved_critical_ambiguities += 1
                errors.append(f"Measure {m_num}: unresolved CRITICAL ambiguity present")
    # 6. Ledger Status & Identity Integrity checks
    ledger_status = ledger.get("ledger_status")
    if ledger_status == "IDENTITY_REVALIDATION_REQUIRED":
        errors.append(
            "Ledger status is IDENTITY_REVALIDATION_REQUIRED: score identity/source binding requires revalidation"
        )
        error_categories.append("IDENTITY_REVALIDATION_REQUIRED")
    elif ledger_status == "REJECTED_SOURCE_MISMATCH":
        errors.append("Ledger status is REJECTED_SOURCE_MISMATCH")
        error_categories.append("REJECTED_SOURCE_MISMATCH")

    # 7. Summary checks
    summary = ledger.get("summary", {})
    summary_verdict = summary.get("source_fidelity_verdict")
    if summary_verdict == "IDENTITY_REVALIDATION_REQUIRED":
        errors.append(
            "Summary source_fidelity_verdict is IDENTITY_REVALIDATION_REQUIRED"
        )
        error_categories.append("IDENTITY_REVALIDATION_REQUIRED")

    summary_compared = summary.get("measures_compared", 0)
    if summary_compared != total_measures:
        errors.append(
            f"Summary measures_compared ({summary_compared}) != total_measures ({total_measures})"
        )
        error_categories.append("INCOMPLETE_COVERAGE")

    rem_critical = summary.get("remaining_critical_discrepancies")
    if rem_critical is None or rem_critical != 0:
        errors.append(
            f"Summary remaining_critical_discrepancies ({rem_critical}) must be exactly 0"
        )
        error_categories.append("CRITICAL_DISCREPANCY_REMAINING")

    if unresolved_critical_ambiguities > 0:
        errors.append(
            f"Found {unresolved_critical_ambiguities} unresolved CRITICAL ambiguities"
        )
        error_categories.append("CRITICAL_AMBIGUITY")

    valid = len(errors) == 0
    if not valid and "IDENTITY_REVALIDATION_REQUIRED" in error_categories:
        verdict = "IDENTITY_REVALIDATION_REQUIRED"
    elif valid:
        verdict = "SOURCE_FIDELITY_VERIFIED"
    else:
        verdict = "PENDING_SOURCE_COMPARISON"
    primary_category = error_categories[0] if error_categories else None

    if not valid and fail_fast:
        error_msg = f"Source fidelity gate failed for {score_id} ({len(errors)} errors): " + "; ".join(errors[:5])
        if len(errors) > 5:
            error_msg += f" ... (+{len(errors)-5} more)"
        raise SourceFidelityGateError(error_msg)

    return FidelityValidationResult(
        valid=valid,
        score_id=score_id,
        canonical_work_id=c_work_id,
        total_measures=total_measures,
        measures_compared=compared_count,
        remaining_critical_discrepancies=rem_critical or 0,
        unresolved_critical_ambiguities=unresolved_critical_ambiguities,
        fidelity_status=verdict,
        error_category=primary_category,
        errors=errors,
    )

"""RC-013 Source-to-Symbolic Fidelity Verification and Audit Gate Engine.

Enforces fail-closed, cryptographic, measure-by-measure source fidelity gates:
- Validates per-measure source comparison ledgers against frozen source manifests.
- Enforces 100% measure comparison completion.
- Disallows PENDING_HUMAN_REVIEW and unreviewed element fields.
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
) -> FidelityValidationResult:
    """Validates a single score's source comparison ledger against all acceptance rules.

    Raises SourceFidelityGateError if fail_closed=True / on hard rejection.
    """
    errors: list[str] = []
    score_id = str(ledger.get("score_id", ""))
    c_work_id = str(ledger.get("canonical_work_id", ""))
    total_measures = int(ledger.get("total_measures", 0))
    measures = ledger.get("measures", [])

    if manifest_csv_path and not canonical_source_sha:
        manifest_map = load_canonical_source_manifest(manifest_csv_path)
        canonical_source_sha = manifest_map.get(c_work_id) or manifest_map.get(score_id)

    # 1. Source SHA Verification
    ledger_source_sha = ledger.get("source_file_sha256")
    if canonical_source_sha and ledger_source_sha != canonical_source_sha:
        errors.append(
            f"Source SHA mismatch in ledger header: expected {canonical_source_sha}, got {ledger_source_sha}"
        )

    # 2. Symbolic SHA Verification
    ledger_symbolic_sha = ledger.get("symbolic_file_sha256")
    if current_symbolic_sha and ledger_symbolic_sha != current_symbolic_sha:
        errors.append(
            f"Symbolic SHA mismatch (file changed after review): expected {current_symbolic_sha}, got {ledger_symbolic_sha}"
        )

    # 3. Measures count integrity
    if len(measures) != total_measures or total_measures <= 0:
        errors.append(
            f"Measure count mismatch: ledger has {len(measures)} measures, declared total_measures={total_measures}"
        )

    # 4. Per-measure validation
    compared_count = 0
    unresolved_critical_ambiguities = 0

    for idx, m in enumerate(measures, start=1):
        m_num = m.get("measure_number", idx)

        # Check required fields
        m_keys = set(m.keys())
        missing_fields = REQUIRED_MEASURE_FIELDS - m_keys
        if missing_fields:
            errors.append(f"Measure {m_num}: missing required fields: {sorted(missing_fields)}")

        # Source & symbolic SHA matching inside measure record
        if canonical_source_sha and m.get("source_file_sha256") != canonical_source_sha:
            errors.append(
                f"Measure {m_num}: source_file_sha256 mismatch in measure record"
            )
        if current_symbolic_sha and m.get("symbolic_file_sha256") != current_symbolic_sha:
            errors.append(
                f"Measure {m_num}: symbolic_file_sha256 mismatch in measure record"
            )

        # Comparison method
        comp_method = m.get("comparison_method")
        if comp_method == "PENDING_HUMAN_REVIEW":
            errors.append(f"Measure {m_num}: comparison_method is PENDING_HUMAN_REVIEW")
        elif comp_method in {"HUMAN_MEASURE_COMPARISON", "HUMAN_NOTE_BY_NOTE"}:
            compared_count += 1
        else:
            errors.append(f"Measure {m_num}: invalid or unrecognized comparison_method: {comp_method}")

        # Element statuses
        for status_key in ELEMENT_STATUS_FIELDS:
            st = m.get(status_key)
            if st == "NOT_REVIEWED":
                errors.append(f"Measure {m_num}: {status_key} is NOT_REVIEWED")
            elif st == "DISCREPANCY":
                errors.append(f"Measure {m_num}: {status_key} has uncorrected DISCREPANCY")
            elif st not in VALID_TERMINAL_ELEMENT_STATUSES:
                errors.append(f"Measure {m_num}: {status_key} has invalid status {st}")

        # Ambiguity check
        if m.get("unresolved_ambiguity") is True:
            sev = m.get("ambiguity_severity")
            if sev == "CRITICAL":
                unresolved_critical_ambiguities += 1
                errors.append(f"Measure {m_num}: unresolved CRITICAL ambiguity present")

    # 5. Summary checks
    summary = ledger.get("summary", {})
    summary_compared = summary.get("measures_compared", 0)
    if summary_compared != total_measures:
        errors.append(
            f"Summary measures_compared ({summary_compared}) != total_measures ({total_measures})"
        )

    rem_critical = summary.get("remaining_critical_discrepancies")
    if rem_critical is None or rem_critical != 0:
        errors.append(
            f"Summary remaining_critical_discrepancies ({rem_critical}) must be exactly 0"
        )

    if unresolved_critical_ambiguities > 0:
        errors.append(
            f"Found {unresolved_critical_ambiguities} unresolved CRITICAL ambiguities"
        )

    valid = len(errors) == 0
    verdict = "SOURCE_FIDELITY_VERIFIED" if valid else "PENDING_SOURCE_COMPARISON"

    if not valid:
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
        errors=errors,
    )

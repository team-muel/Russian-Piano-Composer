"""RC-013 canonical cross-artifact and work-identity integrity gate."""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, cast

import music21 as m21
import yaml

from russian_piano_composer.corpus.rc013_validator import RC013ScoreValidator


@dataclass
class CanonicalIntegrityResult:
    score_id: str
    canonical_work_id: str
    artifact_consistent: bool
    identity_required: bool
    identity_valid: bool
    status: str
    errors: list[str] = field(default_factory=list)


def compute_sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _norm_title(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "", text)


def load_identity_map(
    path: str = "data/manifests/rc013_arensky_identity_map.json",
) -> dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def _find_identity(identity_map: dict[str, Any], score_id: str) -> dict[str, Any] | None:
    for item in identity_map.get("movements", {}).values():
        if item.get("score_id") == score_id:
            return cast(dict[str, Any], item)
    return None


def validate_identity_fields(
    expected: dict[str, Any],
    *,
    movement: int,
    title: str,
    key_fifths: int | None,
    source_file_sha256: str,
) -> list[str]:
    errors: list[str] = []
    if movement != int(expected["movement"]):
        errors.append(f"IDENTITY_MOVEMENT_MISMATCH:{movement}!={expected['movement']}")
    if _norm_title(expected["title"]) not in _norm_title(title):
        errors.append(f"IDENTITY_TITLE_MISMATCH:{title!r}!~{expected['title']!r}")
    if key_fifths != int(expected["key_fifths"]):
        errors.append(f"IDENTITY_KEY_MISMATCH:{key_fifths}!={expected['key_fifths']}")
    if source_file_sha256 != str(expected["source_file_sha256"]):
        errors.append("IDENTITY_SOURCE_SHA_MISMATCH")
    return errors


def validate_canonical_score_integrity(
    score_id: str,
    *,
    identity_map_path: str = "data/manifests/rc013_arensky_identity_map.json",
    digitization_manifest_path: str = "data/manifests/rc013_digitization_manifest.yaml",
    error_log_path: str = "data/manifests/rc013_error_log.json",
    reviews_dir: str = "data/reviews/rc013",
    score_path: str | None = None,
    review_path: str | None = None,
    ledger_path: str | None = None,
) -> CanonicalIntegrityResult:
    with open(digitization_manifest_path, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    entries = {
        str(e["relative_score_path"]).rsplit("/", 1)[-1].replace(".musicxml", ""): e
        for e in manifest.get("score_entries", [])
    }
    if score_id not in entries:
        return CanonicalIntegrityResult(
            score_id,
            "",
            False,
            False,
            False,
            "CROSS_ARTIFACT_INTEGRITY_FAILED",
            ["MANIFEST_ENTRY_MISSING"],
        )

    entry = entries[score_id]
    canonical_work_id = str(entry["canonical_work_id"])
    score_path = score_path or str(entry["relative_score_path"])
    review_path = review_path or os.path.join(reviews_dir, f"{score_id}.review.json")
    ledger_path = ledger_path or os.path.join(reviews_dir, f"{score_id}.source_comparison.json")

    errors: list[str] = []
    for path, label in (
        (score_path, "SCORE"),
        (review_path, "REVIEW"),
        (ledger_path, "LEDGER"),
        (error_log_path, "ERROR_LOG"),
    ):
        if not os.path.exists(path):
            errors.append(f"CROSS_{label}_MISSING:{path}")

    if errors:
        return CanonicalIntegrityResult(
            score_id,
            canonical_work_id,
            False,
            False,
            False,
            "CROSS_ARTIFACT_INTEGRITY_FAILED",
            errors,
        )

    with open(review_path, encoding="utf-8") as f:
        review = json.load(f)
    with open(ledger_path, encoding="utf-8") as f:
        ledger = json.load(f)
    with open(error_log_path, encoding="utf-8") as f:
        error_log = json.load(f)

    report: dict[str, Any] | None = None
    for item in error_log.get("reports", []):
        normalized = str(item.get("file_path", "")).replace("\\", "/")
        if os.path.basename(normalized) == os.path.basename(score_path):
            report = item
            break
    if report is None:
        errors.append("CROSS_ERROR_LOG_ENTRY_MISSING")

    live_sha = compute_sha256_file(score_path)
    sha_claims = {
        "manifest": entry.get("file_sha256"),
        "review": review.get("symbolic_file_sha256"),
        "ledger": ledger.get("symbolic_file_sha256"),
        "error_log": report.get("file_sha256") if report else None,
    }
    for name, value in sha_claims.items():
        if value != live_sha:
            errors.append(f"CROSS_SYMBOLIC_SHA_MISMATCH:{name}:{value}!={live_sha}")

    validation = RC013ScoreValidator().validate_file(
        score_path,
        enforce_anti_synthetic=False,
    )
    live_counts = (
        validation.num_measures,
        validation.num_notes,
        validation.num_rests,
    )
    count_claims = {
        "manifest": (
            entry.get("num_measures"),
            entry.get("num_notes"),
            entry.get("num_rests"),
        ),
        "review": (
            review.get("measures_in_musicxml"),
            review.get("notes_in_musicxml"),
            review.get("rests_in_musicxml"),
        ),
        "error_log": (
            report.get("num_measures"),
            report.get("num_notes"),
            report.get("num_rests"),
        ) if report else (None, None, None),
    }
    for name, value in count_claims.items():
        if value != live_counts:
            errors.append(f"CROSS_COUNT_MISMATCH:{name}:{value}!={live_counts}")

    for name, value in {
        "review": review.get("canonical_work_id"),
        "ledger": ledger.get("canonical_work_id"),
    }.items():
        if value != canonical_work_id:
            errors.append(
                f"CROSS_WORK_ID_MISMATCH:{name}:{value}!={canonical_work_id}"
            )

    source_sha = str(entry.get("source_file_sha256", ""))
    for name, value in {
        "review": review.get("source_file_sha256"),
        "ledger": ledger.get("source_file_sha256"),
    }.items():
        if value != source_sha:
            errors.append(f"CROSS_SOURCE_SHA_MISMATCH:{name}:{value}!={source_sha}")

    if int(entry.get("movement", -1)) != int(review.get("movement", -2)):
        errors.append("CROSS_MOVEMENT_MISMATCH:manifest!=review")
    if _norm_title(entry.get("title")) != _norm_title(review.get("title")):
        errors.append(
            f"CROSS_TITLE_MISMATCH:{entry.get('title')!r}!={review.get('title')!r}"
        )

    artifact_consistent = not errors

    identity_map = load_identity_map(identity_map_path)
    expected = _find_identity(identity_map, score_id)
    identity_required = expected is not None
    identity_errors: list[str] = []

    if expected is not None:
        try:
            parsed = m21.converter.parse(score_path)
            key_signatures = list(
                parsed.recurse().getElementsByClass(m21.key.KeySignature)
            )
            key_fifths = (
                int(key_signatures[0].sharps) if key_signatures else None
            )
            metadata_title = (
                str(parsed.metadata.title or "")
                if getattr(parsed, "metadata", None) is not None
                else ""
            )
        except Exception as exc:
            identity_errors.append(f"IDENTITY_SCORE_PARSE_FAILED:{exc}")
            key_fifths = None
            metadata_title = ""

        identity_errors.extend(
            validate_identity_fields(
                expected,
                movement=int(entry.get("movement", -1)),
                title=metadata_title or str(entry.get("title", "")),
                key_fifths=key_fifths,
                source_file_sha256=source_sha,
            )
        )

    identity_valid = not identity_errors
    all_errors = errors + identity_errors

    if not artifact_consistent:
        status = "CROSS_ARTIFACT_INTEGRITY_FAILED"
    elif identity_required and not identity_valid:
        status = "IDENTITY_REVALIDATION_REQUIRED"
    else:
        status = "PASS"

    return CanonicalIntegrityResult(
        score_id=score_id,
        canonical_work_id=canonical_work_id,
        artifact_consistent=artifact_consistent,
        identity_required=identity_required,
        identity_valid=identity_valid,
        status=status,
        errors=all_errors,
    )

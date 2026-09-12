"""
Corpus manifest parsing, fail-closed validation, role filtering, and logical hashing.
"""
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from russian_piano_composer.domain.corpus import (
    CorpusFormat,
    CorpusRole,
    CorpusSource,
    LicenseClaim,
    PianoMedium,
    ProvenanceStatus,
    ReadinessStatus,
    RightsStatus,
    ScopeCompleteness,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

MANIFEST_SCHEMA_VERSION: int = 1
_ALLOWED_MANIFEST_KEYS: set[str] = {"manifest_version", "sources"}


@dataclass(frozen=True, slots=True)
class CorpusManifest:
    """
    Validated container holding the canonical corpus registrations.
    """
    manifest_version: int
    sources: tuple[CorpusSource, ...]

    def __post_init__(self) -> None:
        if self.manifest_version != MANIFEST_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported manifest version {self.manifest_version}. Expected {MANIFEST_SCHEMA_VERSION}."
            )
        seen_ids: set[str] = set()
        for src in self.sources:
            if not isinstance(src, CorpusSource):
                raise TypeError(f"Manifest source must be CorpusSource instance, got {type(src).__name__}.")
            if src.corpus_id in seen_ids:
                raise ValueError(f"Duplicate corpus_id detected in manifest: {src.corpus_id!r}.")
            seen_ids.add(src.corpus_id)

    def generative_sources(self) -> tuple[CorpusSource, ...]:
        """
        Returns strictly sources registered with role GENERATIVE_RUSSIAN. Fail-closed: control/provisional data never leaks here.
        """
        return tuple(s for s in self.sources if s.role == CorpusRole.GENERATIVE_RUSSIAN)

    def control_sources(self) -> tuple[CorpusSource, ...]:
        """
        Returns strictly sources registered with role CONTROL_NON_RUSSIAN.
        """
        return tuple(s for s in self.sources if s.role == CorpusRole.CONTROL_NON_RUSSIAN)

    def provisional_sources(self) -> tuple[CorpusSource, ...]:
        """
        Returns strictly sources registered with role PROVISIONAL.
        """
        return tuple(s for s in self.sources if s.role == CorpusRole.PROVISIONAL)

    def excluded_sources(self) -> tuple[CorpusSource, ...]:
        """
        Returns strictly sources registered with role EXCLUDED.
        """
        return tuple(s for s in self.sources if s.role == CorpusRole.EXCLUDED)

    def get_source(self, corpus_id: str) -> CorpusSource:
        """
        Retrieve a registered CorpusSource by corpus_id. Raises KeyError if not found.
        """
        for src in self.sources:
            if src.corpus_id == corpus_id:
                return src
        raise KeyError(f"Corpus source not found in manifest: {corpus_id!r}.")

    def compute_manifest_hash(self) -> str:
        """
        Computes a deterministic 64-character SHA-256 fingerprint of the logical manifest.
        Insensitive to YAML whitespace or formatting changes.
        """
        sorted_sources = sorted(self.sources, key=lambda s: s.corpus_id)
        canonical_data: list[dict[str, Any]] = []

        for s in sorted_sources:
            claims_data = [
                {
                    "source_type": claim.source_type,
                    "value": claim.value,
                    "source_url": claim.source_url,
                }
                for claim in sorted(s.license_claims, key=lambda c: (c.source_type, c.value))
            ]
            entry: dict[str, Any] = {
                "corpus_id": s.corpus_id,
                "title": s.title,
                "role": s.role.value,
                "composer": s.composer,
                "source_provider": s.source_provider,
                "source_repository": s.source_repository,
                "source_version": s.source_version,
                "repertoire_scope": s.repertoire_scope,
                "license": s.license,
                "license_claims": claims_data,
                "is_non_commercial": s.is_non_commercial,
                "readiness_status": s.readiness_status.value,
                "scope_completeness": s.scope_completeness.value,
                "verified_at": s.verified_at,
                "composer_authority_ids": s.composer_authority_ids,
                "piano_medium": s.piano_medium.value,
                "coverage_notes": s.coverage_notes,
                "is_complete_for_claimed_scope": s.is_complete_for_claimed_scope,
                "representative_of_full_composer_output": s.representative_of_full_composer_output,
                "score_entry_ids": list(s.score_entry_ids),
                "catalog_groups": list(s.catalog_groups),
                "work_count": s.work_count,
                "piece_count": s.piece_count,
                "score_entry_count": s.score_entry_count,
                "musical_piece_count": s.musical_piece_count,
                "work_cycle_count": s.work_cycle_count,
                "catalog_group_count": s.catalog_group_count,
                "variation_number_count": s.variation_number_count,
                "source_file_count": s.source_file_count,
                "notation_score_file_count": s.notation_score_file_count,
                "tabular_artifact_file_count": s.tabular_artifact_file_count,
                "source_commit": s.source_commit,
                "meta_repository_commit": s.meta_repository_commit,
                "source_documentation": s.source_documentation,
                "doi": s.doi,
                "citation": s.citation,
                "license_url": s.license_url,
                "rights_notes": s.rights_notes,
                "rights_status": s.rights_status.value,
                "rights_review_required": s.rights_review_required,
                "provenance_status": s.provenance_status.value,
                "formats_available": [fmt.value for fmt in s.formats_available],
                "retrieval_method": s.retrieval_method,
                "notes": s.notes,
            }
            canonical_data.append(entry)

        payload = {
            "manifest_version": self.manifest_version,
            "sources": canonical_data,
        }
        canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode()).hexdigest()


def _parse_source_entry(raw: dict[str, Any]) -> CorpusSource:
    if not isinstance(raw, dict):
        raise ValueError(f"Corpus source entry must be a dictionary, got {type(raw).__name__}.")

    try:
        role = CorpusRole(raw["role"])
    except (KeyError, ValueError) as e:
        raise ValueError(f"Invalid or missing role in manifest source {raw.get('corpus_id')!r}: {e}") from e

    try:
        rights_status = RightsStatus(raw.get("rights_status", "VERIFIED"))
    except ValueError as e:
        raise ValueError(f"Invalid rights_status in source {raw.get('corpus_id')!r}: {e}") from e

    try:
        provenance_status = ProvenanceStatus(raw.get("provenance_status", "VERIFIED_SOURCE"))
    except ValueError as e:
        raise ValueError(f"Invalid provenance_status in source {raw.get('corpus_id')!r}: {e}") from e

    try:
        readiness_status = ReadinessStatus(raw.get("readiness_status", "REVIEW_REQUIRED"))
    except ValueError as e:
        raise ValueError(f"Invalid readiness_status in source {raw.get('corpus_id')!r}: {e}") from e

    try:
        scope_completeness = ScopeCompleteness(raw.get("scope_completeness", "COMPLETE_FOR_DECLARED_SCOPE"))
    except ValueError as e:
        raise ValueError(f"Invalid scope_completeness in source {raw.get('corpus_id')!r}: {e}") from e

    try:
        piano_medium = PianoMedium(raw.get("piano_medium", "SOLO_PIANO"))
    except ValueError as e:
        raise ValueError(f"Invalid piano_medium in source {raw.get('corpus_id')!r}: {e}") from e

    raw_formats: Sequence[Any] = raw.get("formats_available", ())
    formats: list[CorpusFormat] = []
    for fmt_str in raw_formats:
        try:
            formats.append(CorpusFormat(fmt_str))
        except ValueError as e:
            raise ValueError(f"Invalid CorpusFormat {fmt_str!r} in source {raw.get('corpus_id')!r}: {e}") from e

    raw_claims: Sequence[dict[str, Any]] = raw.get("license_claims", ())
    license_claims: list[LicenseClaim] = []
    for c in raw_claims:
        if not isinstance(c, dict) or "source_type" not in c or "value" not in c:
            raise ValueError(f"Invalid LicenseClaim dictionary in source {raw.get('corpus_id')!r}: {c!r}")
        license_claims.append(
            LicenseClaim(
                source_type=c["source_type"],
                value=c["value"],
                source_url=c.get("source_url"),
            )
        )

    score_entry_ids = tuple(str(x) for x in raw.get("score_entry_ids", ()))
    catalog_groups = tuple(str(x) for x in raw.get("catalog_groups", ()))

    return CorpusSource(
        corpus_id=raw["corpus_id"],
        title=raw["title"],
        role=role,
        composer=raw["composer"],
        source_provider=raw["source_provider"],
        source_repository=raw["source_repository"],
        source_version=str(raw["source_version"]),
        repertoire_scope=raw["repertoire_scope"],
        license=raw["license"],
        verified_at=str(raw["verified_at"]),
        license_claims=tuple(license_claims),
        is_non_commercial=bool(raw.get("is_non_commercial", True)),
        readiness_status=readiness_status,
        scope_completeness=scope_completeness,
        composer_authority_ids=dict(raw.get("composer_authority_ids", {})),
        piano_medium=piano_medium,
        coverage_notes=raw.get("coverage_notes"),
        is_complete_for_claimed_scope=bool(raw.get("is_complete_for_claimed_scope", False)),
        representative_of_full_composer_output=bool(raw.get("representative_of_full_composer_output", False)),
        score_entry_ids=score_entry_ids,
        catalog_groups=catalog_groups,
        work_count=raw.get("work_count"),
        piece_count=raw.get("piece_count"),
        score_entry_count=raw.get("score_entry_count"),
        musical_piece_count=raw.get("musical_piece_count"),
        work_cycle_count=raw.get("work_cycle_count"),
        catalog_group_count=raw.get("catalog_group_count"),
        variation_number_count=raw.get("variation_number_count"),
        source_file_count=raw.get("source_file_count"),
        notation_score_file_count=raw.get("notation_score_file_count"),
        tabular_artifact_file_count=raw.get("tabular_artifact_file_count"),
        source_commit=raw.get("source_commit"),
        meta_repository_commit=raw.get("meta_repository_commit"),
        source_documentation=raw.get("source_documentation"),
        doi=raw.get("doi"),
        citation=raw.get("citation"),
        license_url=raw.get("license_url"),
        rights_notes=raw.get("rights_notes"),
        rights_status=rights_status,
        rights_review_required=bool(raw.get("rights_review_required", False)),
        provenance_status=provenance_status,
        formats_available=tuple(formats),
        retrieval_method=raw.get("retrieval_method", "git_clone"),
        notes=raw.get("notes"),
    )


def load_manifest(path: Path | str) -> CorpusManifest:
    """
    Loads and validates the YAML corpus manifest, enforcing fail-closed schema validation.
    """
    manifest_path = Path(path)
    if not manifest_path.exists() or not manifest_path.is_file():
        raise FileNotFoundError(f"Corpus manifest file not found: {manifest_path}")

    with open(manifest_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Corpus manifest top-level structure must be a dict, got {type(data).__name__}.")

    unknown_keys = set(data.keys()) - _ALLOWED_MANIFEST_KEYS
    if unknown_keys:
        raise ValueError(f"Corpus manifest contains unknown top-level key(s): {sorted(unknown_keys)}")

    if "manifest_version" not in data:
        raise ValueError("Corpus manifest missing required key 'manifest_version'.")

    manifest_version = data["manifest_version"]
    if manifest_version != MANIFEST_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported manifest_version {manifest_version}. Expected {MANIFEST_SCHEMA_VERSION}."
        )

    if "sources" not in data or not isinstance(data["sources"], list):
        raise ValueError("Corpus manifest missing or invalid 'sources' list.")

    sources_list: list[CorpusSource] = []
    for entry in data["sources"]:
        sources_list.append(_parse_source_entry(entry))

    return CorpusManifest(
        manifest_version=manifest_version,
        sources=tuple(sources_list),
    )

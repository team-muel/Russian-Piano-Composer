"""
Symbolic score ingestion module.

Ingests verified raw score notation files into canonical score domain objects, validates pitch
and exact rational rhythm invariants, computes piece and corpus semantic hashes, exports interim
Parquet tables, and outputs ingestion receipts.
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd

from russian_piano_composer.corpus.adapters.dcml_ms3 import (
    ingest_score_entry_from_ms3,
    resolve_score_file,
)
from russian_piano_composer.corpus.hashing import sha256_file
from russian_piano_composer.corpus.ingestion_models import IngestionReceipt
from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.domain.corpus import CorpusSource
from russian_piano_composer.domain.score import (
    CANONICAL_SCORE_SCHEMA_VERSION,
    CanonicalScore,
    EventKind,
)

EXPECTED_MANIFEST_HASH = "cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212"


@dataclass(frozen=True, slots=True)
class IngestionResult:
    """
    Report for a corpus symbolic score ingestion run.
    """

    corpus_id: str
    status: Literal["COMPLETE", "INCOMPLETE", "FAILED"]
    receipt: IngestionReceipt | None
    scores: tuple[CanonicalScore, ...] = ()
    message: str = ""


def ingest_corpus(
    source: CorpusSource,
    manifest_hash: str,
    raw_base_dir: Path = Path("data/raw"),
    interim_base_dir: Path = Path("data/interim/canonical"),
) -> IngestionResult:
    """
    Ingest all expected score entries for a single corpus source.
    """
    if source.source_commit is None:
        return IngestionResult(
            corpus_id=source.corpus_id,
            status="FAILED",
            receipt=None,
            message="Source has no pinned source_commit",
        )

    raw_repo_dir = raw_base_dir / source.corpus_id / source.source_commit / "repository"
    if not raw_repo_dir.exists():
        return IngestionResult(
            corpus_id=source.corpus_id,
            status="FAILED",
            receipt=None,
            message=f"Raw repository directory missing: {raw_repo_dir}",
        )

    output_dir = interim_base_dir / manifest_hash / source.corpus_id

    expected_ids = set(source.score_entry_ids)
    ingested_scores: list[CanonicalScore] = []
    piece_hashes: dict[str, str] = {}
    warnings: list[str] = []
    failed_count = 0

    print(f"Ingesting {len(source.score_entry_ids)} score entries for {source.corpus_id}...")
    for entry_id in source.score_entry_ids:
        try:
            score_file = resolve_score_file(raw_repo_dir, entry_id)
            score_sha = sha256_file(score_file)
            score = ingest_score_entry_from_ms3(
                corpus_id=source.corpus_id,
                corpus_role=source.role,
                score_entry_id=entry_id,
                composer=source.composer,
                title=f"{source.title} - {entry_id}",
                repo_dir=raw_repo_dir,
                source_repository=source.source_repository,
                source_commit=source.source_commit,
                source_sha256=score_sha,
                manifest_hash=manifest_hash,
            )
            ingested_scores.append(score)
            p_hash = score.compute_piece_hash()
            piece_hashes[entry_id] = p_hash
        except Exception as e:
            failed_count += 1
            warn_msg = f"Failed to ingest entry '{entry_id}': {e}"
            print(f"  [ERROR] {warn_msg}")
            warnings.append(warn_msg)

    ingested_ids = {s.score_entry_id for s in ingested_scores}
    missing_ids = expected_ids - ingested_ids
    if missing_ids:
        err_msg = f"Missing expected score entry IDs: {sorted(missing_ids)}"
        warnings.append(err_msg)

    status: Literal["COMPLETE", "INCOMPLETE", "FAILED"] = (
        "COMPLETE" if not missing_ids and failed_count == 0 else "INCOMPLETE"
    )

    # Compute corpus canonical hash
    corpus_hasher = hashlib.sha256()
    for entry_id in sorted(piece_hashes.keys()):
        corpus_hasher.update(f"{entry_id}:{piece_hashes[entry_id]}\n".encode())
    corpus_canonical_hash = corpus_hasher.hexdigest()

    parser_name = ingested_scores[0].parser_name if ingested_scores else "ms3"
    parser_version = ingested_scores[0].parser_version if ingested_scores else "unknown"

    receipt = IngestionReceipt(
        corpus_id=source.corpus_id,
        source_commit=source.source_commit,
        manifest_hash=manifest_hash,
        canonical_schema_version=CANONICAL_SCORE_SCHEMA_VERSION,
        parser=parser_name,
        parser_version=parser_version,
        expected_score_entries=source.score_entry_count or len(source.score_entry_ids),
        ingested_score_entries=len(ingested_scores),
        failed_score_entries=failed_count,
        status=status,
        warnings=tuple(warnings),
        piece_hashes=piece_hashes,
        corpus_canonical_hash=corpus_canonical_hash,
    )

    # Export Parquet tables
    if ingested_scores:
        output_dir.mkdir(parents=True, exist_ok=True)
        export_canonical_parquet(output_dir, ingested_scores)
        receipt.save_json(output_dir / "ingestion_receipt.json")

    return IngestionResult(
        corpus_id=source.corpus_id,
        status=status,
        receipt=receipt,
        scores=tuple(ingested_scores),
        message=f"Ingested {len(ingested_scores)}/{len(source.score_entry_ids)} score entries (Status: {status}).",
    )


def export_canonical_parquet(output_dir: Path, scores: list[CanonicalScore]) -> None:
    """
    Export lists of CanonicalScore objects to interim Parquet tables with exact rational timing columns.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pieces_rows = []
    measures_rows = []
    events_rows = []

    for score in scores:
        p_hash = score.compute_piece_hash()
        note_count = sum(1 for e in score.events if e.event_kind == EventKind.NOTE)
        rest_count = sum(1 for e in score.events if e.event_kind == EventKind.REST)
        grace_count = sum(1 for e in score.events if e.is_grace)

        pieces_rows.append({
            "piece_id": score.piece_id,
            "corpus_id": score.corpus_id,
            "corpus_role": score.corpus_role.value,
            "score_entry_id": score.score_entry_id,
            "composer": score.composer,
            "title": score.title,
            "source_relative_path": score.source_relative_path,
            "source_sha256": score.source_sha256,
            "source_commit": score.source_commit,
            "manifest_hash": score.manifest_hash,
            "canonical_schema_version": score.canonical_schema_version,
            "parser_name": score.parser_name,
            "parser_version": score.parser_version,
            "measure_count": len(score.measures),
            "event_count": len(score.events),
            "note_count": note_count,
            "rest_count": rest_count,
            "grace_note_count": grace_count,
            "canonical_piece_hash": p_hash,
        })

        for m in score.measures:
            measures_rows.append({
                "piece_id": m.piece_id,
                "measure_index": m.measure_index,
                "source_measure_label": m.source_measure_label,
                "global_onset_num": m.global_onset.numerator,
                "global_onset_den": m.global_onset.denominator,
                "actual_duration_num": m.actual_duration.numerator,
                "actual_duration_den": m.actual_duration.denominator,
                "meter_numerator": m.time_signature.numerator,
                "meter_denominator": m.time_signature.denominator,
                "expected_duration_num": m.expected_duration.numerator,
                "expected_duration_den": m.expected_duration.denominator,
                "is_pickup": m.is_pickup,
            })

        for e in score.events:
            events_rows.append({
                "piece_id": e.piece_id,
                "corpus_id": score.corpus_id,
                "corpus_role": score.corpus_role.value,
                "event_id": e.event_id,
                "event_index": e.event_index,
                "event_kind": e.event_kind.value,
                "measure_index": e.measure_index,
                "source_measure_label": e.source_measure_label,
                "staff": e.staff,
                "voice": e.voice,
                "onset_num": e.global_onset.numerator,
                "onset_den": e.global_onset.denominator,
                "offset_num": e.offset_in_measure.numerator,
                "offset_den": e.offset_in_measure.denominator,
                "duration_num": e.duration.numerator,
                "duration_den": e.duration.denominator,
                "pitch_letter": e.pitch.letter.name if e.pitch else None,
                "pitch_alteration": e.pitch.alteration if e.pitch else None,
                "pitch_octave": e.pitch.octave if e.pitch else None,
                "midi": e.midi,
                "is_grace": e.is_grace,
                "tie_state": e.tie_state.value,
                "source_relative_path": e.source_relative_path,
                "source_event_locator": e.source_event_locator,
            })

    pd.DataFrame(pieces_rows).to_parquet(output_dir / "pieces.parquet", index=False)
    pd.DataFrame(measures_rows).to_parquet(output_dir / "measures.parquet", index=False)
    pd.DataFrame(events_rows).to_parquet(output_dir / "events.parquet", index=False)


def ingest_all_corpora(
    manifest_path: Path = Path("data/manifests/corpus_manifest.yaml"),
    raw_base_dir: Path = Path("data/raw"),
    interim_base_dir: Path = Path("data/interim/canonical"),
) -> list[IngestionResult]:
    """
    Ingest all corpora registered in manifest into canonical symbolic score representation.
    """
    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    if manifest_hash != EXPECTED_MANIFEST_HASH:
        raise ValueError(
            f"Manifest hash mismatch: expected {EXPECTED_MANIFEST_HASH}, got {manifest_hash}"
        )

    results: list[IngestionResult] = []
    for src in manifest.sources:
        print(f"\nProcessing symbolic score ingestion for {src.corpus_id}...")
        res = ingest_corpus(
            source=src,
            manifest_hash=manifest_hash,
            raw_base_dir=raw_base_dir,
            interim_base_dir=interim_base_dir,
        )
        results.append(res)
    return results

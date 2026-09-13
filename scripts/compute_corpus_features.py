"""
Corpus feature computation pipeline.

Reads ingested canonical Parquet tables, reconstructs CanonicalScore objects,
extracts per-piece descriptive features, and exports a feature matrix.

Usage:
    .venv\\Scripts\\python.exe scripts/compute_corpus_features.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fractions import Fraction

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.features import CorpusFeatureMatrix
from russian_piano_composer.domain.score import (
    CANONICAL_SCORE_SCHEMA_VERSION,
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
    TieState,
)
from russian_piano_composer.features import (
    FEATURE_REGISTRY,
    extract_piece_features,
)
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch

EXPECTED_MANIFEST_HASH = "cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212"

# Mapping from pitch letter names to PitchLetter enum
_LETTER_MAP: dict[str, PitchLetter] = {
    "C": PitchLetter.C,
    "D": PitchLetter.D,
    "E": PitchLetter.E,
    "F": PitchLetter.F,
    "G": PitchLetter.G,
    "A": PitchLetter.A,
    "B": PitchLetter.B,
}


def reconstruct_score_from_parquet(
    pieces_df: pd.DataFrame,
    measures_df: pd.DataFrame,
    events_df: pd.DataFrame,
    piece_id: str,
    corpus_source: object,
) -> CanonicalScore:
    """Reconstruct a CanonicalScore from Parquet DataFrames for a single piece."""
    piece_row = pieces_df[pieces_df["piece_id"] == piece_id].iloc[0]

    # Reconstruct measures
    piece_measures_df = measures_df[measures_df["piece_id"] == piece_id].sort_values(
        "measure_index"
    )
    measures: list[CanonicalMeasure] = []
    for _, m in piece_measures_df.iterrows():
        measures.append(
            CanonicalMeasure(
                piece_id=piece_id,
                measure_index=int(m["measure_index"]),
                source_measure_label=str(m["source_measure_label"]),
                global_onset=Fraction(int(m["global_onset_num"]), int(m["global_onset_den"])),
                actual_duration=Fraction(
                    int(m["actual_duration_num"]), int(m["actual_duration_den"])
                ),
                time_signature=TimeSignature(
                    int(m["meter_numerator"]), int(m["meter_denominator"])
                ),
                expected_duration=Fraction(
                    int(m["expected_duration_num"]), int(m["expected_duration_den"])
                ),
                is_pickup=bool(m["is_pickup"]),
            )
        )

    # Reconstruct events
    piece_events_df = events_df[events_df["piece_id"] == piece_id].sort_values(
        ["onset_num", "measure_index", "staff", "voice", "event_kind", "event_index"]
    )
    events: list[CanonicalScoreEvent] = []
    for _, e in piece_events_df.iterrows():
        event_kind = EventKind(str(e["event_kind"]))

        pitch: SpelledPitch | None = None
        midi: int | None = None
        if event_kind == EventKind.NOTE:
            letter_str = str(e["pitch_letter"])
            letter = _LETTER_MAP[letter_str]
            alteration = int(e["pitch_alteration"])
            octave = int(e["pitch_octave"])
            pitch = SpelledPitch(letter=letter, alteration=alteration, octave=octave)
            midi = int(e["midi"])

        onset_frac = Fraction(int(e["onset_num"]), int(e["onset_den"]))

        events.append(
            CanonicalScoreEvent(
                piece_id=piece_id,
                event_id=str(e["event_id"]),
                event_index=int(e["event_index"]),
                event_kind=event_kind,
                measure_index=int(e["measure_index"]),
                source_measure_label=str(e["source_measure_label"]),
                staff=int(e["staff"]),
                voice=int(e["voice"]),
                global_onset=onset_frac,
                offset_in_measure=Fraction(int(e["offset_num"]), int(e["offset_den"])),
                duration=Fraction(int(e["duration_num"]), int(e["duration_den"])),
                pitch=pitch,
                midi=midi,
                is_grace=bool(e["is_grace"]),
                tie_state=TieState(str(e["tie_state"])),
                source_relative_path=str(e.get("source_relative_path", "")),
                source_event_locator=str(e.get("source_event_locator", "")),
            )
        )

    # Sort events deterministically (same as CanonicalScore validation)
    events.sort(
        key=lambda ev: (
            ev.global_onset,
            ev.measure_index,
            ev.staff,
            ev.voice,
            ev.event_kind.value,
            ev.event_index,
        )
    )

    return CanonicalScore(
        piece_id=piece_id,
        corpus_id=str(piece_row["corpus_id"]),
        corpus_role=CorpusRole(str(piece_row["corpus_role"])),
        score_entry_id=str(piece_row["score_entry_id"]),
        composer=str(piece_row["composer"]),
        title=str(piece_row["title"]),
        source_repository=str(piece_row.get("source_repository", "")),
        source_commit=str(piece_row["source_commit"]),
        source_relative_path=str(piece_row["source_relative_path"]),
        source_sha256=str(piece_row["source_sha256"]),
        manifest_hash=str(piece_row["manifest_hash"]),
        parser_version=str(piece_row["parser_version"]),
        measures=tuple(measures),
        events=tuple(events),
        canonical_schema_version=CANONICAL_SCORE_SCHEMA_VERSION,
        parser_name=str(piece_row["parser_name"]),
    )


def main() -> None:
    """Run the corpus feature computation pipeline."""
    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    interim_base = Path("data/interim/canonical")

    print("Loading corpus manifest...")
    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()

    if manifest_hash != EXPECTED_MANIFEST_HASH:
        print(f"ERROR: Manifest hash mismatch: {manifest_hash} != {EXPECTED_MANIFEST_HASH}")
        sys.exit(1)

    print(f"Manifest hash: {manifest_hash}")
    print(f"Sources: {len(manifest.sources)}")

    all_features = []
    total_pieces = 0

    for source in manifest.sources:
        corpus_dir = interim_base / manifest_hash / source.corpus_id
        if not corpus_dir.exists():
            print(f"  SKIP {source.corpus_id}: no canonical data at {corpus_dir}")
            continue

        print(f"\nProcessing {source.corpus_id} ({source.role.value})...")

        pieces_df = pd.read_parquet(corpus_dir / "pieces.parquet")
        measures_df = pd.read_parquet(corpus_dir / "measures.parquet")
        events_df = pd.read_parquet(corpus_dir / "events.parquet")

        piece_ids = sorted(pieces_df["piece_id"].unique())
        print(f"  {len(piece_ids)} pieces")

        for pid in piece_ids:
            try:
                score = reconstruct_score_from_parquet(
                    pieces_df, measures_df, events_df, str(pid), source
                )
                pfs = extract_piece_features(score, manifest_hash)
                all_features.append(pfs)
                total_pieces += 1
            except Exception as e:
                print(f"  ERROR extracting features for {pid}: {e}")

    print("\n--- Feature Extraction Complete ---")
    print(f"Total pieces: {total_pieces}")
    print(f"Features per piece: {len(FEATURE_REGISTRY)}")

    # Build CorpusFeatureMatrix
    matrix = CorpusFeatureMatrix(
        pieces=tuple(all_features),
        manifest_hash=manifest_hash,
        feature_registry=FEATURE_REGISTRY,
    )
    matrix_hash = matrix.compute_matrix_hash()
    print(f"Feature matrix hash: {matrix_hash}")

    # Export to Parquet
    output_dir = Path("data/interim/features") / manifest_hash
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build DataFrame
    rows = []
    for pfs in all_features:
        row: dict[str, object] = {
            "piece_id": pfs.piece_id,
            "corpus_id": pfs.corpus_id,
            "corpus_role": pfs.corpus_role,
            "canonical_piece_hash": pfs.canonical_piece_hash,
        }
        row.update(pfs.features)
        rows.append(row)

    df = pd.DataFrame(rows)
    parquet_path = output_dir / "corpus_features.parquet"
    df.to_parquet(parquet_path, index=False)
    print(f"Exported: {parquet_path}")

    # Export summary JSON
    role_groups = df.groupby("corpus_role")
    summary: dict[str, object] = {
        "manifest_hash": manifest_hash,
        "feature_schema_version": 1,
        "feature_matrix_hash": matrix_hash,
        "total_pieces": total_pieces,
        "feature_count": len(FEATURE_REGISTRY),
        "groups": {},
    }

    groups_dict: dict[str, object] = {}
    for role, group_df in role_groups:
        feature_stats: dict[str, object] = {}
        for fd in FEATURE_REGISTRY:
            col = fd.feature_id
            if col in group_df.columns:
                vals = group_df[col].dropna()
                if len(vals) > 0:
                    feature_stats[col] = {
                        "mean": round(float(vals.mean()), 4),
                        "std": round(float(vals.std()), 4),
                        "min": round(float(vals.min()), 4),
                        "max": round(float(vals.max()), 4),
                        "count": len(vals),
                    }
        groups_dict[str(role)] = {
            "piece_count": len(group_df),
            "features": feature_stats,
        }
    summary["groups"] = groups_dict

    summary_path = output_dir / "corpus_features_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    print(f"Exported: {summary_path}")

    # Print human-readable summary
    print(f"\n{'='*70}")
    print("CORPUS FEATURE SUMMARY")
    print(f"{'='*70}")
    for role_name, role_data in sorted(groups_dict.items()):
        role_info = role_data  # type: ignore[assignment]
        print(f"\n  {role_name}: {role_info['piece_count']} pieces")  # type: ignore[index]
        feat_data = role_info["features"]  # type: ignore[index]
        for fid in ["pitch_range_semitones", "pitch_mean_midi", "pitch_class_entropy",
                     "interval_mean_abs_semitones", "interval_leap_ratio",
                     "rhythm_duration_mean", "density_notes_per_measure"]:
            if fid in feat_data:  # type: ignore[operator]
                stats = feat_data[fid]  # type: ignore[index]
                print(f"    {fid}: mean={stats['mean']}, std={stats['std']}")  # type: ignore[index]
    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()

"""
True Two-Process Reproducibility Verification Script for CTU Pipeline.

Launches two independent Python subprocess workers.
Each worker independently loads the manifest, loads all 141 scores from disk,
runs CTU discovery, builds matched control pairs, and runs held-out validation.
Compares exact detailed outputs, complete pair records, and lineage hashes between Process A and Process B.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

WORKER_SCRIPT = """
import hashlib
import json
import sys
from pathlib import Path
from fractions import Fraction
import pandas as pd

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.domain.score import (
    CANONICAL_SCORE_SCHEMA_VERSION,
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    CorpusRole,
    EventKind,
    TieState,
)
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch
from russian_piano_composer.ctu.controls import build_matched_control_pairs
from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.models import (
    compute_candidate_set_hash,
    compute_control_pair_set_hash,
    compute_ctu_schema_semantic_hash,
    compute_segment_representation_semantic_hash,
    compute_similarity_semantic_hash,
    compute_validation_semantic_hash,
)
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy, CTUValidationPolicy
from russian_piano_composer.ctu.validation import validate_ctu_future_reuse


def load_canonical_score_from_parquet(corpus_dir: Path, target_piece_id: str) -> CanonicalScore:
    df_pieces = pd.read_parquet(corpus_dir / "pieces.parquet")
    p_row = df_pieces[df_pieces["piece_id"] == target_piece_id].iloc[0]

    df_measures = pd.read_parquet(corpus_dir / "measures.parquet")
    p_measures = df_measures[df_measures["piece_id"] == target_piece_id].sort_values("measure_index")

    df_events = pd.read_parquet(corpus_dir / "events.parquet")
    p_events = df_events[df_events["piece_id"] == target_piece_id].sort_values("event_index")

    measures: list[CanonicalMeasure] = []
    for _, m_row in p_measures.iterrows():
        measures.append(
            CanonicalMeasure(
                piece_id=str(m_row["piece_id"]),
                measure_index=int(m_row["measure_index"]),
                source_measure_label=str(m_row["source_measure_label"]),
                global_onset=Fraction(int(m_row["global_onset_num"]), int(m_row["global_onset_den"])),
                actual_duration=Fraction(int(m_row["actual_duration_num"]), int(m_row["actual_duration_den"])),
                time_signature=TimeSignature(int(m_row["meter_numerator"]), int(m_row["meter_denominator"])),
                expected_duration=Fraction(int(m_row["expected_duration_num"]), int(m_row["expected_duration_den"])),
                is_pickup=bool(m_row["is_pickup"]),
            )
        )

    events: list[CanonicalScoreEvent] = []
    for _, e_row in p_events.iterrows():
        p_letter = e_row["pitch_letter"]
        pitch = None
        if pd.notna(p_letter) and p_letter:
            pitch = SpelledPitch(
                letter=PitchLetter[str(p_letter)],
                alteration=int(e_row["pitch_alteration"]),
                octave=int(e_row["pitch_octave"]),
            )

        midi_val = int(e_row["midi"]) if pd.notna(e_row["midi"]) else None

        events.append(
            CanonicalScoreEvent(
                piece_id=str(e_row["piece_id"]),
                event_id=str(e_row["event_id"]),
                event_index=int(e_row["event_index"]),
                event_kind=EventKind(str(e_row["event_kind"])),
                measure_index=int(e_row["measure_index"]),
                source_measure_label=str(e_row["source_measure_label"]),
                staff=int(e_row["staff"]),
                voice=int(e_row["voice"]),
                global_onset=Fraction(int(e_row["onset_num"]), int(e_row["onset_den"])),
                offset_in_measure=Fraction(int(e_row["offset_num"]), int(e_row["offset_den"])),
                duration=Fraction(int(e_row["duration_num"]), int(e_row["duration_den"])),
                pitch=pitch,
                midi=midi_val,
                is_grace=bool(e_row["is_grace"]),
                tie_state=TieState(str(e_row["tie_state"])),
                source_relative_path=str(e_row["source_relative_path"]),
                source_event_locator=str(e_row["source_event_locator"]),
            )
        )

    return CanonicalScore(
        piece_id=str(p_row["piece_id"]),
        corpus_id=str(p_row["corpus_id"]),
        corpus_role=CorpusRole(str(p_row["corpus_role"])),
        score_entry_id=str(p_row["score_entry_id"]),
        composer=str(p_row["composer"]),
        title=str(p_row["title"]),
        source_repository="http://dummy",
        source_commit=str(p_row["source_commit"]),
        source_relative_path=str(p_row["source_relative_path"]),
        source_sha256=str(p_row["source_sha256"]),
        manifest_hash=str(p_row["manifest_hash"]),
        parser_version=str(p_row["parser_version"]),
        measures=tuple(measures),
        events=tuple(events),
        canonical_schema_version=int(p_row.get("canonical_schema_version", CANONICAL_SCORE_SCHEMA_VERSION)),
        parser_name=str(p_row.get("parser_name", "ms3")),
    )


def run_worker(out_json_path: str) -> None:
    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    interim_base = Path("data/interim/canonical") / manifest_hash

    disc_policy = CTUDiscoveryPolicy()
    val_policy = CTUValidationPolicy()

    scores_by_id = {}
    discovery_results = []
    piece_hashes = {}
    detailed_pairs_records = []

    for source in manifest.sources:
        corpus_dir = interim_base / source.corpus_id
        for entry_id in source.score_entry_ids:
            piece_id = f"{source.corpus_id}:{entry_id}"
            score = load_canonical_score_from_parquet(corpus_dir, piece_id)
            scores_by_id[piece_id] = score
            piece_hashes[piece_id] = score.compute_piece_hash()
            disc_res = discover_ctus_for_score(score, manifest_hash=manifest_hash, policy=disc_policy)
            discovery_results.append(disc_res)

            pairs = build_matched_control_pairs(score, disc_res, val_policy, manifest_hash)
            for p in pairs:
                detailed_pairs_records.append({
                    "piece_id": piece_id,
                    "candidate_id": p.target_candidate_id,
                    "target_span": [p.target_ctu.span.start.measure_index, p.target_ctu.span.end.measure_index],
                    "target_rep_hash": p.target_ctu.representation_hash,
                    "target_disc_score": p.target_ctu.discovery_score,
                    "control_id": p.control_candidate.candidate_id if p.control_candidate else None,
                    "control_span": [p.control_candidate.span.start.measure_index, p.control_candidate.span.end.measure_index] if p.control_candidate else None,
                    "control_rep_hash": p.control_candidate.representation_hash if p.control_candidate else None,
                    "is_available": p.is_available,
                })

    val_res = validate_ctu_future_reuse(scores_by_id, tuple(discovery_results), manifest_hash, disc_policy, val_policy)

    payload = {
        "manifest_hash": manifest_hash,
        "piece_ids": sorted(list(scores_by_id.keys())),
        "piece_hashes": piece_hashes,
        "schema_semantic_hash": compute_ctu_schema_semantic_hash(),
        "representation_semantic_hash": compute_segment_representation_semantic_hash(),
        "similarity_semantic_hash": compute_similarity_semantic_hash(),
        "validation_semantic_hash": compute_validation_semantic_hash(),
        "discovery_policy_hash": disc_policy.compute_policy_hash(),
        "validation_policy_hash": val_policy.compute_policy_hash(),
        "candidate_set_hash": val_res.candidate_set_hash,
        "control_pair_set_hash": val_res.control_pair_set_hash,
        "validation_result_hash": val_res.compute_validation_result_hash(),
        "mean_ctu_future_score": val_res.mean_ctu_future_score,
        "mean_control_future_score": val_res.mean_control_future_score,
        "mean_difference": val_res.mean_difference,
        "cohens_d": val_res.cohens_d,
        "bootstrap_ci": [val_res.bootstrap_ci_lower, val_res.bootstrap_ci_upper],
        "permutation_p_value": val_res.permutation_p_value,
        "permutation_extreme_count": val_res.permutation_extreme_count,
        "permutation_iterations": val_res.permutation_iterations,
        "empirical_status": val_res.empirical_status.value,
        "total_requested_controls": val_res.total_requested_controls,
        "valid_matched_controls": val_res.valid_matched_controls,
        "unavailable_controls": val_res.unavailable_controls,
        "detailed_pairs": detailed_pairs_records,
        "piece_records": [
            {
                "piece_id": r.piece_id,
                "ctu": r.ctu_mean_future_score,
                "ctrl": r.control_mean_future_score,
                "diff": r.difference,
                "matched_pairs": r.matched_pair_count,
                "unavailable": r.unavailable_control_count,
            }
            for r in val_res.piece_records
        ]
    }

    # Compute process payload hash over complete canonical payload json
    payload_encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["process_payload_hash"] = hashlib.sha256(payload_encoded).hexdigest()

    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    run_worker(sys.argv[1])
"""


def main() -> None:
    print("--- Running True Two-Process Reproducibility Audit ---")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        worker_code_path = tmp_path / "worker.py"
        out_a_path = tmp_path / "out_a.json"
        out_b_path = tmp_path / "out_b.json"

        worker_code_path.write_text(WORKER_SCRIPT, encoding="utf-8")

        import os
        worker_env = os.environ.copy()
        worker_env["PYTHONPATH"] = "src"

        # Launch Worker Process A
        print("Launching Process A...")
        proc_a = subprocess.run(
            [sys.executable, str(worker_code_path), str(out_a_path)],
            capture_output=True,
            text=True,
            check=False,
            env=worker_env,
        )
        if proc_a.returncode != 0:
            print(f"Process A FAILED:\n{proc_a.stderr}")
            sys.exit(1)

        # Launch Worker Process B
        print("Launching Process B...")
        proc_b = subprocess.run(
            [sys.executable, str(worker_code_path), str(out_b_path)],
            capture_output=True,
            text=True,
            check=False,
            env=worker_env,
        )
        if proc_b.returncode != 0:
            print(f"Process B FAILED:\n{proc_b.stderr}")
            sys.exit(1)

        with open(out_a_path, encoding="utf-8") as f:
            data_a = json.load(f)

        with open(out_b_path, encoding="utf-8") as f:
            data_b = json.load(f)

        payload_hash_a = data_a.get("process_payload_hash", "")
        payload_hash_b = data_b.get("process_payload_hash", "")

        # Compare exact keys and values between Process A and Process B
        mismatches = []
        for key in data_a:
            if data_a[key] != data_b.get(key):
                mismatches.append(f"Field mismatch for '{key}': A={data_a[key]} vs B={data_b.get(key)}")

        if mismatches or payload_hash_a != payload_hash_b:
            print("REPRODUCIBILITY ERROR: Mismatches found between Process A and Process B:")
            for m in mismatches:
                print(f"  - {m}")
            if payload_hash_a != payload_hash_b:
                print(f"  - Payload hash mismatch: Process A={payload_hash_a} vs Process B={payload_hash_b}")
            sys.exit(1)

        print("\n--- TRUE TWO-PROCESS REPRODUCIBILITY AUDIT: PASS ---")
        print(f"  Processed Pieces:           {len(data_a['piece_ids'])} / 141")
        print(f"  Process A Payload Hash:     {payload_hash_a}")
        print(f"  Process B Payload Hash:     {payload_hash_b}")
        print(f"  Candidate Set Hash:         {data_a['candidate_set_hash']}")
        print(f"  Control Pair Set Hash:      {data_a['control_pair_set_hash']}")
        print(f"  Validation Result Hash:     {data_a['validation_result_hash']}")
        print(f"  CTU Schema Semantic Hash:   {data_a['schema_semantic_hash']}")
        print(f"  Representation Sem. Hash:   {data_a['representation_semantic_hash']}")
        print(f"  Similarity Semantic Hash:   {data_a['similarity_semantic_hash']}")
        print(f"  Validation Semantic Hash:   {data_a['validation_semantic_hash']}")
        print(f"  Discovery Policy Hash:      {data_a['discovery_policy_hash']}")
        print(f"  Validation Policy Hash:     {data_a['validation_policy_hash']}")
        print(f"  Empirical Status:           {data_a['empirical_status']}")


if __name__ == "__main__":
    main()

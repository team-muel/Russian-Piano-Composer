import sys
from fractions import Fraction
from pathlib import Path

import pandas as pd

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.models import compute_candidate_set_hash
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy, CTUValidationPolicy
from russian_piano_composer.ctu.validation import validate_ctu_future_reuse
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



def main() -> None:
    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    if not manifest_path.exists():
        print("Error: corpus_manifest.yaml not found.")
        sys.exit(1)

    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    interim_base = Path("data/interim/canonical") / manifest_hash

    if not interim_base.exists():
        print("Error: Canonical corpus parquet cache not found.")
        sys.exit(1)

    disc_policy = CTUDiscoveryPolicy()
    val_policy = CTUValidationPolicy()

    print("--- Auditing CTU Pipeline Invariants across Full 141-Piece Corpus ---")

    # Load all 141 pieces for full audit
    scores_by_id = {}
    for source in manifest.sources:
        corpus_dir = interim_base / source.corpus_id
        if not corpus_dir.exists():
            raise FileNotFoundError(f"Missing corpus dir: {corpus_dir}")

        for entry_id in source.score_entry_ids:
            piece_id = f"{source.corpus_id}:{entry_id}"
            score = load_canonical_score_from_parquet(corpus_dir, piece_id)
            scores_by_id[piece_id] = score

    if len(scores_by_id) != 141:
        raise RuntimeError(f"Audit failed: Expected 141 pieces, loaded {len(scores_by_id)}")

    # Audit 1: Temporal Anti-Leakage across ALL 141 pieces
    total_retained = 0
    for _pid, score in scores_by_id.items():
        res = discover_ctus_for_score(score, manifest_hash=manifest_hash, policy=disc_policy)
        total_retained += len(res.retained_ctus)
        for ctu in res.retained_ctus:
            assert ctu.span.end.measure_index <= res.discovery_measures, (
                f"LEAKAGE ERROR: Candidate {ctu.candidate_id} end measure ({ctu.span.end.measure_index}) "
                f"extends into future region ({res.discovery_measures})"
            )

    print(f"Audit 1: Temporal Anti-Leakage -> PASS (0 candidate spans extend into future region across {len(scores_by_id)} pieces, {total_retained} retained CTUs)")

    # Audit 2: Deterministic Hash and Statistical Reproducibility across ALL 141 pieces
    res1_list = [discover_ctus_for_score(s, manifest_hash=manifest_hash, policy=disc_policy) for s in scores_by_id.values()]
    res2_list = [discover_ctus_for_score(s, manifest_hash=manifest_hash, policy=disc_policy) for s in scores_by_id.values()]

    cand_set_hash1 = compute_candidate_set_hash(res1_list)
    cand_set_hash2 = compute_candidate_set_hash(res2_list)
    assert cand_set_hash1 == cand_set_hash2, f"Candidate set hash mismatch: {cand_set_hash1} vs {cand_set_hash2}"

    val1 = validate_ctu_future_reuse(scores_by_id, tuple(res1_list), manifest_hash, disc_policy, val_policy)
    val2 = validate_ctu_future_reuse(scores_by_id, tuple(res2_list), manifest_hash, disc_policy, val_policy)

    val_hash1 = val1.compute_validation_result_hash()
    val_hash2 = val2.compute_validation_result_hash()
    assert val_hash1 == val_hash2, f"Validation result hash mismatch: {val_hash1} vs {val_hash2}"

    assert val1.mean_difference == val2.mean_difference, "Validation diff mismatch"
    assert val1.permutation_p_value == val2.permutation_p_value, "Permutation p mismatch"
    assert val1.empirical_status == val2.empirical_status, "Empirical status mismatch"

    print("Audit 2: Deterministic Reproducibility -> PASS (100% hash match across 141 pieces)")
    print(f"  Candidate Set Hash:     {cand_set_hash1}")
    print(f"  Validation Result Hash: {val_hash1}")

    # Audit 3: Forbidden Code Inspection Safeguard
    forbidden_modules = [
        "russian_piano_composer.corpus.theme_annotations",
        "russian_piano_composer.domain.annotations",
    ]
    for mod in sys.modules:
        for fmod in forbidden_modules:
            if mod.startswith(fmod):
                raise RuntimeError(f"ROLE-BLINDNESS AUDIT ERROR: Forbidden annotation module {mod} loaded in environment!")

    print("Audit 3: Zero Ground Truth / Annotation Leakage -> PASS (no annotation or candidate spec modules imported)")
    print("\n--- ALL CTU PIPELINE INVARIANTS VERIFIED CLEAN ACROSS FULL CORPUS ---")


if __name__ == "__main__":
    main()

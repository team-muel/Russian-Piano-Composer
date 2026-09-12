#!/usr/bin/env python3
"""
Data Integrity Audit Script for RC-007A Acceptance.
Programmatically recomputes and verifies all scientific invariants across the six corpora.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import ms3
import pandas as pd
import pyarrow  # Ensure direct pyarrow import check

from russian_piano_composer.corpus.acquisition import (
    EXPECTED_MANIFEST_HASH,
    acquire_corpus_source,
)
from russian_piano_composer.corpus.hashing import sha256_file
from russian_piano_composer.corpus.ingestion_models import AcquisitionReceipt, IngestionReceipt
from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.score import CANONICAL_SCORE_SCHEMA_VERSION
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


def audit_rc007() -> int:
    print("==================================================================")
    print("   RC-007A -- Acquisition / Ingestion Acceptance Integrity Audit   ")
    print("==================================================================\n")

    # 1. Manifest verification
    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    print(f"[OK] Loaded Manifest: {manifest_path}")
    print(f"[OK] Manifest Hash:   {manifest_hash}")
    assert manifest_hash == EXPECTED_MANIFEST_HASH, f"Manifest hash mismatch: {manifest_hash}"

    # 2. Environment runtime versions
    print("\n--- Runtime Environment Versions ---")
    print(f"  Python Version:           {sys.version.split()[0]}")
    print(f"  ms3 Version:              {getattr(ms3, '__version__', 'unknown')}")
    print(f"  pandas Version:           {pd.__version__}")
    print(f"  pyarrow Version:          {pyarrow.__version__}")
    print(f"  Canonical Schema Version: {CANONICAL_SCORE_SCHEMA_VERSION}")

    # 3. Local Raw Repository Checkout & Receipt Audit
    print("\n--- Local Raw Repository Checkout & Receipt Audit ---")
    raw_base = Path("data/raw")
    total_mismatches = 0

    for src in manifest.sources:
        print(f"\nCorpus: {src.corpus_id}")
        target_dir = raw_base / src.corpus_id / src.source_commit
        repo_dir = target_dir / "repository"
        receipt_path = target_dir / "acquisition_receipt.json"

        assert receipt_path.exists(), f"Missing acquisition receipt for {src.corpus_id}"
        receipt = AcquisitionReceipt.load_json(receipt_path)

        assert receipt.source_commit == src.source_commit, f"Commit mismatch in receipt for {src.corpus_id}"
        assert receipt.manifest_hash == manifest_hash, f"Manifest hash mismatch in receipt for {src.corpus_id}"

        # Audit local git repository
        git_origin = subprocess.run(["git", "remote", "get-url", "origin"], cwd=repo_dir, capture_output=True, text=True, check=True).stdout.strip()
        git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, capture_output=True, text=True, check=True).stdout.strip()
        git_status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True, check=True).stdout.strip()

        print(f"  Git Origin:      {git_origin}")
        print(f"  Git HEAD:        {git_head}")
        print(f"  Working Tree:    {'CLEAN' if not git_status else 'DIRTY'}")

        assert git_head == src.source_commit, f"HEAD mismatch for {src.corpus_id}: got {git_head}, expected {src.source_commit}"
        assert not git_status, f"Dirty working tree in raw repo for {src.corpus_id}"

        # Audit artifact hashes
        mismatches = 0
        for art in receipt.artifacts:
            art_file = repo_dir / art.relative_path
            if not art_file.exists() or art_file.stat().st_size != art.size_bytes or sha256_file(art_file) != art.sha256:
                mismatches += 1

        print(f"  Receipt Artifacts Count:  {receipt.artifact_count}")
        print(f"  Hash-Verified Artifacts:  {receipt.artifact_count - mismatches}")
        print(f"  Artifact Mismatches:      {mismatches}")

        total_mismatches += mismatches

    assert total_mismatches == 0, f"Artifact mismatches detected: {total_mismatches}"

    # 4. Canonical Statistics Recomputation & Parquet Audit
    print("\n--- Recomputed Corpus Canonical Statistics & Parquet Audit ---")
    interim_base = Path("data/interim/canonical") / manifest_hash

    table_data = []
    russian_stats = {"corpora": 0, "pieces": 0, "measures": 0, "events": 0, "notes": 0, "rests": 0, "grace": 0}
    control_stats = {"corpora": 0, "pieces": 0, "measures": 0, "events": 0, "notes": 0, "rests": 0, "grace": 0}

    total_pitch_checks = 0
    pitch_mismatches = 0
    empty_piece_failures = 0

    for src in manifest.sources:
        c_dir = interim_base / src.corpus_id
        pieces_df = pd.read_parquet(c_dir / "pieces.parquet")
        measures_df = pd.read_parquet(c_dir / "measures.parquet")
        events_df = pd.read_parquet(c_dir / "events.parquet")
        receipt = IngestionReceipt.load_json(c_dir / "ingestion_receipt.json")

        # Inventory check
        expected_ids = set(src.score_entry_ids)
        ingested_ids = set(pieces_df["score_entry_id"].tolist())
        assert expected_ids == ingested_ids, f"Inventory mismatch for {src.corpus_id}: missing {expected_ids - ingested_ids}"

        # Per-piece non-empty invariant check
        for _, row in pieces_df.iterrows():
            if row["measure_count"] <= 0 or row["event_count"] <= 0 or row["note_count"] <= 0:
                empty_piece_failures += 1

        p_count = len(pieces_df)
        m_count = len(measures_df)
        e_count = len(events_df)
        n_count = int(pieces_df["note_count"].sum())
        r_count = int(pieces_df["rest_count"].sum())
        g_count = int(pieces_df["grace_note_count"].sum())
        t_count = len(events_df[events_df["tie_state"].isin(["START", "CONTINUE", "STOP"])])

        staves = sorted(events_df["staff"].unique().tolist())
        voices = sorted(events_df["voice"].unique().tolist())
        ts_pairs = sorted({(r.meter_numerator, r.meter_denominator) for _, r in measures_df.iterrows()})

        table_data.append({
            "corpus_id": src.corpus_id,
            "role": src.role.value,
            "expected": src.score_entry_count,
            "pieces": p_count,
            "measures": m_count,
            "events": e_count,
            "notes": n_count,
            "rests": r_count,
            "grace": g_count,
            "ties": t_count,
            "staves": staves,
            "voices": voices,
            "time_signatures": ts_pairs,
            "hash": receipt.corpus_canonical_hash,
        })

        if src.role == CorpusRole.GENERATIVE_RUSSIAN:
            russian_stats["corpora"] += 1
            russian_stats["pieces"] += p_count
            russian_stats["measures"] += m_count
            russian_stats["events"] += e_count
            russian_stats["notes"] += n_count
            russian_stats["rests"] += r_count
            russian_stats["grace"] += g_count
        else:
            control_stats["corpora"] += 1
            control_stats["pieces"] += p_count
            control_stats["measures"] += m_count
            control_stats["events"] += e_count
            control_stats["notes"] += n_count
            control_stats["rests"] += r_count
            control_stats["grace"] += g_count

        # Pitch & MIDI validation across all events
        notes_subset = events_df[events_df["event_kind"] == "NOTE"]
        for _, row in notes_subset.iterrows():
            total_pitch_checks += 1
            letter = PitchLetter[row["pitch_letter"]]
            alt = int(row["pitch_alteration"])
            octave = int(row["pitch_octave"])
            sp = SpelledPitch(letter=letter, alteration=alt, octave=octave)
            if sp.midi != int(row["midi"]):
                pitch_mismatches += 1

    assert empty_piece_failures == 0, f"Found {empty_piece_failures} empty canonical pieces"
    assert pitch_mismatches == 0, f"Found {pitch_mismatches} pitch/MIDI mismatches"

    # Print summary table
    print("\n--- Ingestion Statistics Table ---")
    print(f"{'Corpus ID':30s} {'Role':20s} {'Pieces':>7s} {'Measures':>9s} {'Events':>9s} {'Notes':>9s} {'Rests':>7s} {'Grace':>7s} {'Ties':>7s}")
    print("-" * 115)
    for row in table_data:
        print(f"{row['corpus_id']:30s} {row['role']:20s} {row['pieces']:7d} {row['measures']:9d} {row['events']:9d} {row['notes']:9d} {row['rests']:7d} {row['grace']:7d} {row['ties']:7d}")

    print("\n--- Aggregate Role Statistics ---")
    print("GENERATIVE_RUSSIAN:")
    print(f"  Corpora: {russian_stats['corpora']}, Pieces: {russian_stats['pieces']}, Measures: {russian_stats['measures']}, Events: {russian_stats['events']}, Notes: {russian_stats['notes']}, Rests: {russian_stats['rests']}, Grace Notes: {russian_stats['grace']}")
    print("CONTROL_NON_RUSSIAN:")
    print(f"  Corpora: {control_stats['corpora']}, Pieces: {control_stats['pieces']}, Measures: {control_stats['measures']}, Events: {control_stats['events']}, Notes: {control_stats['notes']}, Rests: {control_stats['rests']}, Grace Notes: {control_stats['grace']}")

    print("\n--- Diagnostic Checks ---")
    print(f"  Total Notes Checked for Pitch/MIDI Consistency: {total_pitch_checks}")
    print(f"  Pitch / MIDI Mismatch Count:                   {pitch_mismatches}")
    print(f"  Empty Piece Failures:                          {empty_piece_failures}")

    # 5. Deterministic Audit Samples (Lexicographically first piece per corpus)
    print("\n--- Deterministic Audit Samples (Lexicographically First Score Entry per Corpus) ---")
    for src in manifest.sources:
        sample_id = sorted(src.score_entry_ids)[0]
        c_dir = interim_base / src.corpus_id
        pieces_df = pd.read_parquet(c_dir / "pieces.parquet")
        events_df = pd.read_parquet(c_dir / "events.parquet")
        p_row = pieces_df[pieces_df["score_entry_id"] == sample_id].iloc[0]
        e_sample = events_df[events_df["piece_id"] == p_row["piece_id"]].head(10)

        print(f"\nCorpus: {src.corpus_id} | Sample Entry: {sample_id}")
        print(f"  Source Path: {p_row['source_relative_path']} | SHA-256: {p_row['source_sha256']}")
        print(f"  Piece ID:    {p_row['piece_id']}")
        print(f"  Measures: {p_row['measure_count']} | Events: {p_row['event_count']} | Notes: {p_row['note_count']} | Rests: {p_row['rest_count']} | Grace: {p_row['grace_note_count']}")
        print(f"  Piece Hash:  {p_row['canonical_piece_hash']}")
        print("  First 5 Canonical Events:")
        for _, e in e_sample.head(5).iterrows():
            pitch_info = f"{e['pitch_letter']}{e['pitch_alteration']}{e['pitch_octave']} (MIDI {e['midi']})" if e['event_kind'] == 'NOTE' else "REST"
            onset_f = f"{e['onset_num']}/{e['onset_den']}"
            dur_f = f"{e['duration_num']}/{e['duration_den']}"
            print(f"    - Event {e['event_index']:04d}: Measure {e['measure_index']} | Staff {e['staff']} Voice {e['voice']} | Onset {onset_f} | Dur {dur_f} | {e['event_kind']} {pitch_info} | Tie {e['tie_state']} Grace {e['is_grace']}")

    # 6. Sandboxed Acquisition Tamper Verification
    print("\n--- Sandbox Acquisition Tamper Verification ---")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_raw = Path(tmp_dir) / "raw"
        sample_src = manifest.sources[0]

        # Copy actual acquired raw folder to sandbox
        sandbox_target = tmp_raw / sample_src.corpus_id / sample_src.source_commit
        sandbox_target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["powershell", "Copy-Item", "-Recurse", str(raw_base / sample_src.corpus_id / sample_src.source_commit), str(sandbox_target)],
            check=True,
        )

        # Tamper with one verified artifact file in sandbox
        mscx_files = list((sandbox_target / "repository").rglob("*.mscx"))
        assert len(mscx_files) > 0, "No MSCX files found in sandbox copy"
        tampered_file = mscx_files[0]
        tampered_file.write_text("<TAMPERED_CONTENT/>", encoding="utf-8")

        res_tamper = acquire_corpus_source(sample_src, manifest_hash, raw_base_dir=tmp_raw, verify_only=True)
        print(f"  Tamper Test Result: {res_tamper.status} -- {res_tamper.message}")
        assert res_tamper.status == "FAILED", "Tamper verification failed to detect file modification!"
        assert "mismatch" in res_tamper.message.lower()

    # 7. Git Isolation Check
    print("\n--- Git Isolation Audit ---")
    ls_files = subprocess.run(["git", "ls-files", "data/raw", "data/interim", "data/processed"], capture_output=True, text=True, check=True).stdout.strip()
    print(f"  Git Tracked Raw/Interim Files Count: {len(ls_files.splitlines()) if ls_files else 0}")
    assert not ls_files, f"Git tracked files detected under data/raw or data/interim: {ls_files}"

    print("\n==================================================================")
    print("   RC-007A DATA INTEGRITY AUDIT PASSED WITH 100% INVARIANTS OK   ")
    print("==================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(audit_rc007())

"""
Parser adapter for DCML / ms3 MuseScore notation scores and TSV facets.
"""

import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

import ms3
import pandas as pd

from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.score import (
    CANONICAL_SCORE_SCHEMA_VERSION,
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
    TieState,
)
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch

PITCH_NAME_REGEX = re.compile(r"^([A-G])(#*|b*|x*)(-?\d+)$")


def parse_spelled_pitch_from_name(name_str: str) -> SpelledPitch:
    """
    Parse scientific spelled pitch string (e.g. 'C4', 'C#4', 'Db4', 'F##4', 'Ebb4')
    into a canonical SpelledPitch object.
    """
    match = PITCH_NAME_REGEX.match(name_str)
    if not match:
        raise ValueError(f"Unrecognized spelled pitch format: '{name_str}'")

    letter_char, acc_str, octave_str = match.groups()
    letter = PitchLetter[letter_char]
    octave = int(octave_str)

    alteration = 0
    if "#" in acc_str:
        alteration = len(acc_str)
    elif "b" in acc_str:
        alteration = -len(acc_str)
    elif "x" in acc_str:
        alteration = 2 * len(acc_str)

    return SpelledPitch(letter=letter, alteration=alteration, octave=octave)


def parse_rational(val: Any) -> Fraction:
    """
    Parse a numeric/string/float value into an exact Fraction without binary float distortion.
    """
    if isinstance(val, Fraction):
        return val
    if isinstance(val, int):
        return Fraction(val, 1)
    if isinstance(val, float):
        if math.isnan(val):
            return Fraction(0, 1)
        return Fraction(str(val)).limit_denominator(1920)
    val_str = str(val).strip()
    if "/" in val_str:
        num_str, den_str = val_str.split("/")
        return Fraction(int(num_str), int(den_str))
    return Fraction(val_str).limit_denominator(1920)


def resolve_score_file(repo_dir: Path, score_entry_id: str) -> Path:
    """
    Resolve the single exact MSCX notation score file corresponding to score_entry_id.
    Fail closed if zero or ambiguous multiple score files match.
    """
    direct = repo_dir / f"{score_entry_id}.mscx"
    if direct.exists() and direct.is_file():
        return direct

    ms3_dir = repo_dir / "MS3" / f"{score_entry_id}.mscx"
    if ms3_dir.exists() and ms3_dir.is_file():
        return ms3_dir

    matches = [p for p in repo_dir.rglob(f"{score_entry_id}.mscx") if not any(part.startswith(".") for part in p.parts)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ValueError(f"Ambiguous score resolution for entry '{score_entry_id}': found {len(matches)} files: {matches}")

    # Try matching without exact extension if compressed
    matches_mscz = [p for p in repo_dir.rglob(f"{score_entry_id}.mscz") if not any(part.startswith(".") for part in p.parts)]
    if len(matches_mscz) == 1:
        return matches_mscz[0]

    raise FileNotFoundError(f"Score entry file not found for score_entry_id '{score_entry_id}' in {repo_dir}")


def ingest_score_entry_from_ms3(
    corpus_id: str,
    corpus_role: CorpusRole,
    score_entry_id: str,
    composer: str,
    title: str,
    repo_dir: Path,
    source_repository: str,
    source_commit: str,
    source_sha256: str,
    manifest_hash: str,
) -> CanonicalScore:
    """
    Ingest a single score entry into a CanonicalScore using the ms3 parser.
    """
    piece_id = f"{corpus_id}:{score_entry_id}"
    score_file = resolve_score_file(repo_dir, score_entry_id)
    source_relative_path = score_file.relative_to(repo_dir).as_posix()

    ms3_score = ms3.Score(str(score_file))
    ms3_parser_version = getattr(ms3, "__version__", "unknown")

    measures_df = ms3_score.mscx.measures()
    notes_and_rests_df = ms3_score.mscx.notes_and_rests()

    # Parse measures
    measures_list: list[CanonicalMeasure] = []
    timesig_map: dict[int, TimeSignature] = {}

    curr_timesig = TimeSignature(4, 4)
    for _, row in measures_df.iterrows():
        mc = int(row["mc"])
        measure_idx = mc - 1
        mn_label = str(row.get("mn", mc))

        if pd.notna(row.get("timesig")):
            ts_str = str(row["timesig"]).strip()
            if "/" in ts_str:
                num_s, den_s = ts_str.split("/")
                curr_timesig = TimeSignature(int(num_s), int(den_s))

        timesig_map[measure_idx] = curr_timesig

        global_onset = parse_rational(row.get("quarterbeats", 0))
        actual_dur = parse_rational(row.get("duration_qb", curr_timesig.bar_duration))
        expected_dur = curr_timesig.bar_duration
        dont_count_val = row.get("dont_count")
        is_dont_count = bool(dont_count_val) if pd.notna(dont_count_val) else False
        is_pickup = is_dont_count or (measure_idx == 0 and actual_dur < expected_dur)

        m = CanonicalMeasure(
            piece_id=piece_id,
            measure_index=measure_idx,
            source_measure_label=mn_label,
            global_onset=global_onset,
            actual_duration=actual_dur,
            time_signature=curr_timesig,
            expected_duration=expected_dur,
            is_pickup=is_pickup,
        )
        measures_list.append(m)

    # Sort measures
    measures_list.sort(key=lambda m: m.measure_index)
    measures_tuple = tuple(measures_list)

    # Parse events
    raw_events: list[tuple[Any, ...]] = []
    for row_idx, row in notes_and_rests_df.iterrows():
        mc = int(row["mc"]) if pd.notna(row.get("mc")) else 1
        measure_idx = max(0, mc - 1)
        mn_label = str(row.get("mn", mc))
        staff = int(row["staff"]) if pd.notna(row.get("staff")) else 1
        voice = int(row["voice"]) if pd.notna(row.get("voice")) else 1

        global_onset = parse_rational(row.get("quarterbeats", 0))

        # Calculate offset in measure
        measure_onset = parse_rational(measures_df.loc[measures_df["mc"] == mc, "quarterbeats"].values[0]) if (measures_df["mc"] == mc).any() else Fraction(0)
        offset_in_measure = max(Fraction(0), global_onset - measure_onset)

        # Duration
        dur_qb = row.get("duration_qb")
        dur_val = parse_rational(dur_qb) if pd.notna(dur_qb) else Fraction(1, 4)

        grace_val = row.get("grace")
        is_grace_flag = bool(grace_val) if pd.notna(grace_val) else False
        is_grace = is_grace_flag or (dur_val == Fraction(0))

        # Tie state
        tied_val = row.get("tied")
        tie_state = TieState.NONE
        if pd.notna(tied_val):
            t_int = int(tied_val)
            if t_int == 1:
                tie_state = TieState.START
            elif t_int == -1:
                tie_state = TieState.STOP
            elif t_int == 2:
                tie_state = TieState.CONTINUE

        # Kind & Pitch
        name_val = row.get("name")
        midi_val = row.get("midi")

        if pd.notna(name_val) and pd.notna(midi_val):
            kind = EventKind.NOTE
            pitch = parse_spelled_pitch_from_name(str(name_val))
            midi = int(midi_val)
            if midi != pitch.midi:
                raise ValueError(
                    f"Score entry '{score_entry_id}' row {row_idx}: MIDI mismatch for '{name_val}'. Provided {midi}, computed {pitch.midi}"
                )
        else:
            kind = EventKind.REST
            pitch = None
            midi = None

        locator = f"{source_relative_path}:mc{mc}:staff{staff}:voice{voice}:row{row_idx}"
        raw_events.append((
            global_onset,
            measure_idx,
            staff,
            voice,
            kind,
            mn_label,
            offset_in_measure,
            dur_val,
            pitch,
            midi,
            is_grace,
            tie_state,
            locator,
        ))

    # Sort events deterministically
    raw_events.sort(key=lambda e: (e[0], e[1], e[2], e[3], e[4].value, e[12]))

    canonical_events: list[CanonicalScoreEvent] = []
    for evt_idx, e in enumerate(raw_events):
        event_id = f"{piece_id}:evt_{evt_idx:06d}"
        c_evt = CanonicalScoreEvent(
            piece_id=piece_id,
            event_id=event_id,
            event_index=evt_idx,
            event_kind=e[4],
            measure_index=e[1],
            source_measure_label=e[5],
            staff=e[2],
            voice=e[3],
            global_onset=e[0],
            offset_in_measure=e[6],
            duration=e[7],
            pitch=e[8],
            midi=e[9],
            is_grace=e[10],
            tie_state=e[11],
            source_relative_path=source_relative_path,
            source_event_locator=e[12],
        )
        canonical_events.append(c_evt)

    score = CanonicalScore(
        piece_id=piece_id,
        corpus_id=corpus_id,
        corpus_role=corpus_role,
        score_entry_id=score_entry_id,
        composer=composer,
        title=title,
        source_repository=source_repository,
        source_commit=source_commit,
        source_relative_path=source_relative_path,
        source_sha256=source_sha256,
        manifest_hash=manifest_hash,
        parser_version=ms3_parser_version,
        measures=measures_tuple,
        events=tuple(canonical_events),
        canonical_schema_version=CANONICAL_SCORE_SCHEMA_VERSION,
        parser_name="ms3",
    )
    return score


def load_canonical_score_from_parquet(corpus_dir: Path, target_piece_id: str) -> CanonicalScore:
    """
    Reconstruct a CanonicalScore from saved interim parquet files.
    """
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


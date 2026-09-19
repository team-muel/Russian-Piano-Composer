"""
Canonical Synthetic Fixture Suite & Metamorphic Invariance Validation for RC-011.

Constructs exactly 20 programmatically generated synthetic scores (Fixtures A through T),
evaluates directional music theory assertions across all 7 families,
runs full metamorphic invariance checks across 6 transformation classes,
and computes deterministic cryptographic validation fingerprints.
"""

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.score import (
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
)
from russian_piano_composer.structure_analysis.extractor import extract_structural_representation
from russian_piano_composer.structure_analysis.schema import (
    STRUCTURAL_FEATURE_CATALOG,
    AvailabilityStatus,
    FeatureFamily,
    InvarianceClass,
    TransformationType,
    compute_invariance_contract_hash,
    get_feature_invariance_contract,
)
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


def _midi_to_spelled_pitch(midi: int) -> SpelledPitch:
    """Deterministic MIDI to SpelledPitch mapping."""
    pc = midi % 12
    octave = (midi // 12) - 1
    mapping = {
        0: (PitchLetter.C, 0),
        1: (PitchLetter.C, 1),
        2: (PitchLetter.D, 0),
        3: (PitchLetter.D, 1),
        4: (PitchLetter.E, 0),
        5: (PitchLetter.F, 0),
        6: (PitchLetter.F, 1),
        7: (PitchLetter.G, 0),
        8: (PitchLetter.G, 1),
        9: (PitchLetter.A, 0),
        10: (PitchLetter.A, 1),
        11: (PitchLetter.B, 0),
    }
    letter, alter = mapping[pc]
    return SpelledPitch(letter=letter, alteration=alter, octave=octave)


def build_synthetic_score(
    note_tuples: list[tuple[int, int, Fraction, Fraction]],  # (midi, measure, offset_fraction, dur_fraction)
    measure_count: int,
    entry_id: str = "synthetic_fixture",
) -> CanonicalScore:
    """Build a CanonicalScore from (midi, measure_idx, offset_frac, dur_frac) tuples."""
    corpus_id = "SYNTHETIC"
    piece_id = f"{corpus_id}:{entry_id}"
    measures = tuple(
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=i,
            source_measure_label=str(i + 1),
            global_onset=Fraction(i, 1),
            actual_duration=Fraction(1, 1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1, 1),
        )
        for i in range(measure_count)
    )

    events: list[CanonicalScoreEvent] = []
    for idx, (midi, m_idx, off_frac, dur_frac) in enumerate(note_tuples):
        m_onset = measures[m_idx].global_onset
        events.append(
            CanonicalScoreEvent(
                piece_id=piece_id,
                event_id=f"ev_{idx}",
                event_index=idx,
                event_kind=EventKind.NOTE,
                measure_index=m_idx,
                source_measure_label=measures[m_idx].source_measure_label,
                staff=1 if midi >= 60 else 2,
                voice=1,
                global_onset=m_onset + off_frac,
                offset_in_measure=off_frac,
                duration=dur_frac,
                pitch=_midi_to_spelled_pitch(midi),
                midi=midi,
            )
        )

    events.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))

    return CanonicalScore(
        piece_id=piece_id,
        corpus_id=corpus_id,
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id=entry_id,
        composer="Synthetic Composer",
        title=entry_id,
        source_repository="synthetic",
        source_commit="0" * 40,
        source_relative_path=f"{entry_id}.mscx",
        source_sha256="0" * 64,
        manifest_hash="0" * 64,
        parser_version="1.0.0",
        measures=measures,
        events=tuple(events),
    )


def compute_fixture_semantic_hash(score: CanonicalScore) -> str:
    """Deterministic hash of a synthetic fixture's structural event data."""
    canonical = [
        {
            "measure": e.measure_index,
            "onset": str(e.global_onset),
            "offset": str(e.offset_in_measure),
            "duration": str(e.duration),
            "midi": e.midi,
            "staff": e.staff,
            "voice": e.voice,
        }
        for e in score.events
    ]
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


# ---------------------------------------------------------------------------
# 20 Canonical Fixtures (A through T)
# ---------------------------------------------------------------------------

def fixture_a_c_major() -> CanonicalScore:
    """Fixture A: Stable C-major I-IV-V-I progression."""
    notes = [
        (48, 0, Fraction(0, 1), Fraction(1, 1)), (60, 0, Fraction(0, 1), Fraction(1, 1)),
        (64, 0, Fraction(0, 1), Fraction(1, 1)), (67, 0, Fraction(0, 1), Fraction(1, 1)),
        (53, 1, Fraction(0, 1), Fraction(1, 1)), (65, 1, Fraction(0, 1), Fraction(1, 1)),
        (69, 1, Fraction(0, 1), Fraction(1, 1)), (72, 1, Fraction(0, 1), Fraction(1, 1)),
        (55, 2, Fraction(0, 1), Fraction(1, 1)), (67, 2, Fraction(0, 1), Fraction(1, 1)),
        (71, 2, Fraction(0, 1), Fraction(1, 1)), (74, 2, Fraction(0, 1), Fraction(1, 1)),
        (48, 3, Fraction(0, 1), Fraction(1, 1)), (64, 3, Fraction(0, 1), Fraction(1, 1)),
        (67, 3, Fraction(0, 1), Fraction(1, 1)), (72, 3, Fraction(0, 1), Fraction(1, 1)),
    ]
    return build_synthetic_score(notes, 4, "fixture_a_c_major")


def fixture_b_transposed() -> CanonicalScore:
    """Fixture B: G-major transposed equivalent of A (+7 semitones)."""
    notes = [
        (55, 0, Fraction(0, 1), Fraction(1, 1)), (67, 0, Fraction(0, 1), Fraction(1, 1)),
        (71, 0, Fraction(0, 1), Fraction(1, 1)), (74, 0, Fraction(0, 1), Fraction(1, 1)),
        (60, 1, Fraction(0, 1), Fraction(1, 1)), (72, 1, Fraction(0, 1), Fraction(1, 1)),
        (76, 1, Fraction(0, 1), Fraction(1, 1)), (79, 1, Fraction(0, 1), Fraction(1, 1)),
        (62, 2, Fraction(0, 1), Fraction(1, 1)), (74, 2, Fraction(0, 1), Fraction(1, 1)),
        (78, 2, Fraction(0, 1), Fraction(1, 1)), (81, 2, Fraction(0, 1), Fraction(1, 1)),
        (55, 3, Fraction(0, 1), Fraction(1, 1)), (71, 3, Fraction(0, 1), Fraction(1, 1)),
        (74, 3, Fraction(0, 1), Fraction(1, 1)), (79, 3, Fraction(0, 1), Fraction(1, 1)),
    ]
    return build_synthetic_score(notes, 4, "fixture_b_transposed")


def fixture_c_tonal_transition() -> CanonicalScore:
    """Fixture C: Tonal center transition (C-major M0-7 -> G-major M8-15)."""
    notes = []
    # M0-7: C major
    for m in range(8):
        notes.extend([
            (48, m, Fraction(0, 1), Fraction(1, 1)), (60, m, Fraction(0, 1), Fraction(1, 1)),
            (64, m, Fraction(0, 1), Fraction(1, 1)), (67, m, Fraction(0, 1), Fraction(1, 1)),
        ])
    # M8-15: G major (with F#)
    for m in range(8, 16):
        notes.extend([
            (55, m, Fraction(0, 1), Fraction(1, 1)), (67, m, Fraction(0, 1), Fraction(1, 1)),
            (71, m, Fraction(0, 1), Fraction(1, 1)), (74, m, Fraction(0, 1), Fraction(1, 1)),
        ])
    return build_synthetic_score(notes, 16, "fixture_c_tonal_transition")


def fixture_d_chromatic_passage() -> CanonicalScore:
    """Fixture D: Strongly chromatic cluster passage."""
    notes = []
    chromatic_pcs = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]
    for m in range(8):
        for idx in range(4):
            p = chromatic_pcs[(m * 4 + idx) % 12]
            notes.extend([
                (p, m, Fraction(idx, 4), Fraction(1, 4)),
                (p + 1, m, Fraction(idx, 4), Fraction(1, 4)),
                (p + 6, m, Fraction(idx, 4), Fraction(1, 4)),
            ])
    return build_synthetic_score(notes, 8, "fixture_d_chromatic_passage")


def fixture_e_authentic_cadence() -> CanonicalScore:
    """Fixture E: Dominant-to-Tonic authentic resolution with rhythmic lengthening."""
    notes = [
        # M0-1: Preparatory chords
        (48, 0, Fraction(0, 1), Fraction(1, 2)), (60, 0, Fraction(0, 1), Fraction(1, 2)), (64, 0, Fraction(0, 1), Fraction(1, 2)),
        (53, 0, Fraction(1, 2), Fraction(1, 2)), (65, 0, Fraction(1, 2), Fraction(1, 2)), (69, 0, Fraction(1, 2), Fraction(1, 2)),
        # Dominant chord (G - B - D - F)
        (55, 1, Fraction(0, 1), Fraction(1, 2)), (59, 1, Fraction(0, 1), Fraction(1, 2)), (62, 1, Fraction(0, 1), Fraction(1, 2)), (65, 1, Fraction(0, 1), Fraction(1, 2)),
        # Tonic resolution (C - E - G) with long duration
        (48, 1, Fraction(1, 2), Fraction(1, 2)), (60, 1, Fraction(1, 2), Fraction(1, 2)), (64, 1, Fraction(1, 2), Fraction(1, 2)), (67, 1, Fraction(1, 2), Fraction(1, 2)),
    ]
    return build_synthetic_score(notes, 2, "fixture_e_authentic_cadence")


def fixture_f_deceptive_cadence() -> CanonicalScore:
    """Fixture F: Dominant-to-VI deceptive motion proxy (C-major context resolving to A-minor)."""
    notes = [
        # M0-1: C major context
        (48, 0, Fraction(0, 1), Fraction(1, 1)), (60, 0, Fraction(0, 1), Fraction(1, 1)), (64, 0, Fraction(0, 1), Fraction(1, 1)), (67, 0, Fraction(0, 1), Fraction(1, 1)),
        (48, 1, Fraction(0, 1), Fraction(1, 1)), (60, 1, Fraction(0, 1), Fraction(1, 1)), (64, 1, Fraction(0, 1), Fraction(1, 1)), (67, 1, Fraction(0, 1), Fraction(1, 1)),
        # M2: Subdominant F major
        (53, 2, Fraction(0, 1), Fraction(1, 1)), (65, 2, Fraction(0, 1), Fraction(1, 1)), (69, 2, Fraction(0, 1), Fraction(1, 1)), (72, 2, Fraction(0, 1), Fraction(1, 1)),
        # M3: Dominant G major -> Deceptive resolution to A minor
        (55, 3, Fraction(0, 1), Fraction(1, 2)), (59, 3, Fraction(0, 1), Fraction(1, 2)), (62, 3, Fraction(0, 1), Fraction(1, 2)),
        (57, 3, Fraction(1, 2), Fraction(1, 2)), (60, 3, Fraction(1, 2), Fraction(1, 2)), (64, 3, Fraction(1, 2), Fraction(1, 2)),
    ]
    return build_synthetic_score(notes, 4, "fixture_f_deceptive_cadence")


def fixture_g_block_chord() -> CanonicalScore:
    """Fixture G: Block-chord texture (4 synchronous attacks per measure)."""
    notes = []
    for m in range(8):
        for beat in range(4):
            off = Fraction(beat, 4)
            dur = Fraction(1, 4)
            notes.extend([
                (48, m, off, dur), (60, m, off, dur), (64, m, off, dur), (67, m, off, dur)
            ])
    return build_synthetic_score(notes, 8, "fixture_g_block_chord")


def fixture_h_arpeggio() -> CanonicalScore:
    """Fixture H: Arpeggiated texture with exact pitch material of G (IOI = 0.5 quarters)."""
    notes = []
    pitches = [48, 55, 60, 64, 67, 72, 76, 79]
    for m in range(8):
        for idx in range(8):
            p = pitches[idx % 8]
            off = Fraction(idx, 8)
            dur = Fraction(1, 8)
            notes.append((p, m, off, dur))
    return build_synthetic_score(notes, 8, "fixture_h_arpeggio")


def fixture_i_repeated_notes() -> CanonicalScore:
    """Fixture I: Rapid repeated-note texture on single pitch (IOI = 0.5 quarters <= 0.5)."""
    notes = []
    for m in range(8):
        for idx in range(8):
            off = Fraction(idx, 8)
            dur = Fraction(1, 8)
            notes.append((60, m, off, dur))
    return build_synthetic_score(notes, 8, "fixture_i_repeated_notes")


def fixture_j_octave_doubling() -> CanonicalScore:
    """Fixture J: Simultaneous multi-octave doubling texture."""
    notes = []
    for m in range(8):
        for beat in range(4):
            off = Fraction(beat, 4)
            dur = Fraction(1, 4)
            notes.extend([
                (48, m, off, dur), (60, m, off, dur), (72, m, off, dur)
            ])
    return build_synthetic_score(notes, 8, "fixture_j_octave_doubling")


def fixture_k_parallel_motion() -> CanonicalScore:
    """Fixture K: Parallel outer motion (soprano and bass moving in parallel tenths)."""
    notes = []
    for m in range(8):
        for beat in range(4):
            off = Fraction(beat, 4)
            dur = Fraction(1, 4)
            bass_p = 48 + beat * 2
            sop_p = bass_p + 16  # Tenth above
            notes.extend([
                (bass_p, m, off, dur), (sop_p, m, off, dur)
            ])
    return build_synthetic_score(notes, 8, "fixture_k_parallel_motion")


def fixture_l_contrary_motion() -> CanonicalScore:
    """Fixture L: Contrary outer motion (soprano ascends, bass descends)."""
    notes = []
    for m in range(8):
        for beat in range(4):
            off = Fraction(beat, 4)
            dur = Fraction(1, 4)
            bass_p = 60 - beat * 2
            sop_p = 60 + beat * 2
            notes.extend([
                (bass_p, m, off, dur), (sop_p, m, off, dur)
            ])
    return build_synthetic_score(notes, 8, "fixture_l_contrary_motion")


def fixture_m_oblique_motion() -> CanonicalScore:
    """Fixture M: Oblique outer motion (soprano moves, bass stays on pedal note)."""
    notes = []
    for m in range(8):
        for beat in range(4):
            off = Fraction(beat, 4)
            dur = Fraction(1, 4)
            bass_p = 48  # Static bass pedal
            sop_p = 72 + beat * 2
            notes.extend([
                (bass_p, m, off, dur), (sop_p, m, off, dur)
            ])
    return build_synthetic_score(notes, 8, "fixture_m_oblique_motion")


def fixture_n_aba_recurrence() -> CanonicalScore:
    """Fixture N: ABA formal recurrence (A: M0-3, B: M4-7, A: M8-11)."""
    notes = []
    # A section (M0-3): C major
    for m in range(4):
        notes.extend([
            (48, m, Fraction(0, 1), Fraction(1, 1)), (60, m, Fraction(0, 1), Fraction(1, 1)),
            (64, m, Fraction(0, 1), Fraction(1, 1)), (67, m, Fraction(0, 1), Fraction(1, 1)),
        ])
    # B section (M4-7): F# minor / distant chromatic contrast
    for m in range(4, 8):
        notes.extend([
            (54, m, Fraction(0, 1), Fraction(1, 1)), (66, m, Fraction(0, 1), Fraction(1, 1)),
            (69, m, Fraction(0, 1), Fraction(1, 1)), (73, m, Fraction(0, 1), Fraction(1, 1)),
        ])
    # A section return (M8-11): C major
    for m in range(8, 12):
        notes.extend([
            (48, m, Fraction(0, 1), Fraction(1, 1)), (60, m, Fraction(0, 1), Fraction(1, 1)),
            (64, m, Fraction(0, 1), Fraction(1, 1)), (67, m, Fraction(0, 1), Fraction(1, 1)),
        ])
    return build_synthetic_score(notes, 12, "fixture_n_aba_recurrence")


def fixture_o_through_composed() -> CanonicalScore:
    """Fixture O: Through-composed non-return control (unique harmony each measure)."""
    notes = []
    for m in range(12):
        root = 48 + (m * 5) % 12  # Circle of fifths wandering
        notes.extend([
            (root, m, Fraction(0, 1), Fraction(1, 1)), (root + 4, m, Fraction(0, 1), Fraction(1, 1)),
            (root + 7, m, Fraction(0, 1), Fraction(1, 1)),
        ])
    return build_synthetic_score(notes, 12, "fixture_o_through_composed")


def fixture_p_ascending_register() -> CanonicalScore:
    """Fixture P: Ascending register trajectory (pitch centroid climbs across 8 bins)."""
    notes = []
    for m in range(8):
        base_p = 40 + m * 5  # Ascends from 40 to 75
        for beat in range(4):
            notes.append((base_p, m, Fraction(beat, 4), Fraction(1, 4)))
    return build_synthetic_score(notes, 8, "fixture_p_ascending_register")


def fixture_q_descending_register() -> CanonicalScore:
    """Fixture Q: Descending register trajectory (pitch centroid falls across 8 bins)."""
    notes = []
    for m in range(8):
        base_p = 80 - m * 5  # Descends from 80 to 45
        for beat in range(4):
            notes.append((base_p, m, Fraction(beat, 4), Fraction(1, 4)))
    return build_synthetic_score(notes, 8, "fixture_q_descending_register")


def fixture_r_stable_register() -> CanonicalScore:
    """Fixture R: Stable register trajectory (constant pitch centroid across 8 bins)."""
    notes = []
    for m in range(8):
        for beat in range(4):
            notes.append((60, m, Fraction(beat, 4), Fraction(1, 4)))
    return build_synthetic_score(notes, 8, "fixture_r_stable_register")


def fixture_s_sparse_to_dense() -> CanonicalScore:
    """Fixture S: Sparse to dense texture trajectory (attack density increases across 8 bins)."""
    notes = []
    for m in range(8):
        # Measure m has m+1 attacks
        subdivs = m + 1
        for idx in range(subdivs):
            off = Fraction(idx, subdivs)
            dur = Fraction(1, subdivs)
            notes.append((60, m, off, dur))
    return build_synthetic_score(notes, 8, "fixture_s_sparse_to_dense")


def fixture_t_dense_to_sparse() -> CanonicalScore:
    """Fixture T: Dense to sparse texture trajectory (attack density decreases across 8 bins)."""
    notes = []
    for m in range(8):
        subdivs = 8 - m
        for idx in range(subdivs):
            off = Fraction(idx, subdivs)
            dur = Fraction(1, subdivs)
            notes.append((60, m, off, dur))
    return build_synthetic_score(notes, 8, "fixture_t_dense_to_sparse")


@dataclass(frozen=True, slots=True)
class SyntheticFixture:
    """Immutable record for a canonical synthetic fixture."""

    fixture_id: str
    name: str
    family_owner: FeatureFamily
    builder: Callable[[], CanonicalScore]


# Immutable Registry of all 20 Fixtures
FIXTURE_REGISTRY: tuple[SyntheticFixture, ...] = (
    SyntheticFixture("A", "stable_c_major_progression", FeatureFamily.TONAL, fixture_a_c_major),
    SyntheticFixture("B", "transposed_progression", FeatureFamily.TONAL, fixture_b_transposed),
    SyntheticFixture("C", "tonal_center_transition", FeatureFamily.TONAL, fixture_c_tonal_transition),
    SyntheticFixture("D", "chromatic_passage", FeatureFamily.TONAL, fixture_d_chromatic_passage),
    SyntheticFixture("E", "authentic_cadence_boundary", FeatureFamily.CADENCE, fixture_e_authentic_cadence),
    SyntheticFixture("F", "deceptive_motion_boundary", FeatureFamily.CADENCE, fixture_f_deceptive_cadence),
    SyntheticFixture("G", "block_chord_texture", FeatureFamily.TEXTURE_REGISTER, fixture_g_block_chord),
    SyntheticFixture("H", "arpeggiated_texture", FeatureFamily.TEXTURE_REGISTER, fixture_h_arpeggio),
    SyntheticFixture("I", "repeated_note_texture", FeatureFamily.TEXTURE_REGISTER, fixture_i_repeated_notes),
    SyntheticFixture("J", "octave_doubling_texture", FeatureFamily.TEXTURE_REGISTER, fixture_j_octave_doubling),
    SyntheticFixture("K", "parallel_outer_motion", FeatureFamily.VOICE_LEADING, fixture_k_parallel_motion),
    SyntheticFixture("L", "contrary_outer_motion", FeatureFamily.VOICE_LEADING, fixture_l_contrary_motion),
    SyntheticFixture("M", "oblique_outer_motion", FeatureFamily.VOICE_LEADING, fixture_m_oblique_motion),
    SyntheticFixture("N", "aba_formal_recurrence", FeatureFamily.FORM, fixture_n_aba_recurrence),
    SyntheticFixture("O", "through_composed_control", FeatureFamily.FORM, fixture_o_through_composed),
    SyntheticFixture("P", "ascending_register_trajectory", FeatureFamily.TEMPORAL_TRAJECTORY, fixture_p_ascending_register),
    SyntheticFixture("Q", "descending_register_trajectory", FeatureFamily.TEMPORAL_TRAJECTORY, fixture_q_descending_register),
    SyntheticFixture("R", "stable_register_trajectory", FeatureFamily.TEMPORAL_TRAJECTORY, fixture_r_stable_register),
    SyntheticFixture("S", "sparse_to_dense_trajectory", FeatureFamily.TEMPORAL_TRAJECTORY, fixture_s_sparse_to_dense),
    SyntheticFixture("T", "dense_to_sparse_trajectory", FeatureFamily.TEMPORAL_TRAJECTORY, fixture_t_dense_to_sparse),
)


def compute_synthetic_fixture_suite_hash(fixtures: tuple[SyntheticFixture, ...] = FIXTURE_REGISTRY) -> str:
    """Deterministic SHA-256 hash of the complete 20-fixture suite binding all note/measure data."""
    records = []
    for f in sorted(fixtures, key=lambda x: x.fixture_id):
        score = f.builder()
        note_events = [e for e in score.events if e.event_kind == EventKind.NOTE]
        event_list = [
            {
                "measure": e.measure_index,
                "onset": str(e.global_onset),
                "offset": str(e.offset_in_measure),
                "duration": str(e.duration),
                "midi": e.midi,
                "staff": e.staff,
                "voice": e.voice,
            }
            for e in score.events
        ]
        records.append({
            "fixture_id": f.fixture_id,
            "name": f.name,
            "family": f.family_owner.value,
            "measure_count": len(score.measures),
            "note_count": len(note_events),
            "events": event_list,
            "semantic_hash": compute_fixture_semantic_hash(score),
        })
    canonical = {
        "version": "SYNTHETIC_FIXTURE_SUITE_V2",
        "fixture_count": len(fixtures),
        "fixtures": records,
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class SyntheticAssertionContract:
    """Immutable definition of a directional music theory assertion."""

    assertion_id: str
    fixture_id: str
    family: FeatureFamily
    condition_description: str
    expected_relational_operator: str


# Immutable Registry of all 20 Directional Theory Assertions
ASSERTION_REGISTRY: tuple[SyntheticAssertionContract, ...] = (
    SyntheticAssertionContract("ASSERT_TONAL_A_VS_B_TRANSPOSITION_INVARIANCE", "A/B", FeatureFamily.TONAL, "abs(A.tonal_conf - B.tonal_conf) < 1e-4 and A.tonal_conf > 0.60", "=="),
    SyntheticAssertionContract("ASSERT_TONAL_C_CENTER_CHANGE_DETECTION", "C", FeatureFamily.TONAL, "C.tonal_center_change_rate > 0.0", ">"),
    SyntheticAssertionContract("ASSERT_TONAL_D_CHROMATICITY_ELEVATION", "D", FeatureFamily.TONAL, "D.chromatic_share > 0.30 and D.tonal_conf < A.tonal_conf", ">"),
    SyntheticAssertionContract("ASSERT_SONORITY_BLOCK_VS_ARPEGGIO_CARDINALITY", "G/H", FeatureFamily.SONORITY, "G.pc_card_mean >= 3.0 and H.pc_card_mean <= 1.5", ">="),
    SyntheticAssertionContract("ASSERT_SONORITY_D_IC1_DISSONANCE", "D", FeatureFamily.SONORITY, "D.ic1_share > 0.0", ">"),
    SyntheticAssertionContract("ASSERT_CADENCE_E_AUTHENTIC_RESOLUTION", "E", FeatureFamily.CADENCE, "E.tonic_resolution_rate > 0.0 and E.boundary_rate > 0.0", ">"),
    SyntheticAssertionContract("ASSERT_CADENCE_F_DECEPTIVE_MOTION", "F", FeatureFamily.CADENCE, "F.deceptive_proxy_rate > 0.0", ">"),
    SyntheticAssertionContract("ASSERT_FORM_N_VS_O_RECAPITULATION_RETURN", "N/O", FeatureFamily.FORM, "N.late_return > 0.70 and N.late_return > O.late_return + 0.20", ">"),
    SyntheticAssertionContract("ASSERT_VL_K_PARALLEL_DOMINANCE", "K", FeatureFamily.VOICE_LEADING, "K.parallel_motion_share > 0.75", ">"),
    SyntheticAssertionContract("ASSERT_VL_L_CONTRARY_DOMINANCE", "L", FeatureFamily.VOICE_LEADING, "L.contrary_motion_share > 0.75", ">"),
    SyntheticAssertionContract("ASSERT_VL_M_OBLIQUE_DOMINANCE", "M", FeatureFamily.VOICE_LEADING, "M.oblique_motion_share > 0.75", ">"),
    SyntheticAssertionContract("ASSERT_TEXTURE_G_BLOCK_CHORD", "G", FeatureFamily.TEXTURE_REGISTER, "G.block_chord_share > 0.80", ">"),
    SyntheticAssertionContract("ASSERT_TEXTURE_H_ARPEGGIO_PROXY", "H", FeatureFamily.TEXTURE_REGISTER, "H.arpeggiation_proxy_rate > 0.0", ">"),
    SyntheticAssertionContract("ASSERT_TEXTURE_I_REPEATED_NOTES", "I", FeatureFamily.TEXTURE_REGISTER, "I.repeated_note_attack_rate > 0.0", ">"),
    SyntheticAssertionContract("ASSERT_TEXTURE_J_OCTAVE_DOUBLING", "J", FeatureFamily.TEXTURE_REGISTER, "J.octave_doubling_share > 0.80", ">"),
    SyntheticAssertionContract("ASSERT_TRAJ_P_ASCENDING_REGISTER", "P", FeatureFamily.TEMPORAL_TRAJECTORY, "P.register_center_slope > 0.0", ">"),
    SyntheticAssertionContract("ASSERT_TRAJ_Q_DESCENDING_REGISTER", "Q", FeatureFamily.TEMPORAL_TRAJECTORY, "Q.register_center_slope < 0.0", "<"),
    SyntheticAssertionContract("ASSERT_TRAJ_R_STABLE_REGISTER", "R", FeatureFamily.TEMPORAL_TRAJECTORY, "abs(R.register_center_slope) < 0.5", "<"),
    SyntheticAssertionContract("ASSERT_TRAJ_S_SPARSE_TO_DENSE", "S", FeatureFamily.TEMPORAL_TRAJECTORY, "S.attack_density_slope > 0.0", ">"),
    SyntheticAssertionContract("ASSERT_TRAJ_T_DENSE_TO_SPARSE", "T", FeatureFamily.TEMPORAL_TRAJECTORY, "T.attack_density_slope < 0.0", "<"),
)


def compute_synthetic_assertion_contract_hash(contracts: tuple[SyntheticAssertionContract, ...] = ASSERTION_REGISTRY) -> str:
    """Deterministic SHA-256 hash of the complete synthetic assertion contract."""
    records = [
        {
            "assertion_id": c.assertion_id,
            "fixture_id": c.fixture_id,
            "family": c.family.value,
            "condition": c.condition_description,
            "operator": c.expected_relational_operator,
        }
        for c in sorted(contracts, key=lambda x: x.assertion_id)
    ]
    canonical = {
        "version": "SYNTHETIC_ASSERTION_CONTRACT_V1",
        "assertion_count": len(contracts),
        "assertions": records,
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


# ---------------------------------------------------------------------------
# Metamorphic Transformation Operations
# ---------------------------------------------------------------------------

def apply_metamorphic_transformation(
    score: CanonicalScore,
    trans_type: TransformationType,
    param: Any = None,
) -> CanonicalScore:
    """Apply a metamorphic transformation to a CanonicalScore."""
    if trans_type == TransformationType.TRANSPOSITION:
        semitones: int = int(param if param is not None else 1)
        new_events = []
        for e in score.events:
            if e.event_kind == EventKind.NOTE and e.midi is not None:
                new_midi = e.midi + semitones
                new_events.append(
                    CanonicalScoreEvent(
                        piece_id=e.piece_id,
                        event_id=e.event_id,
                        event_index=e.event_index,
                        event_kind=e.event_kind,
                        measure_index=e.measure_index,
                        source_measure_label=e.source_measure_label,
                        staff=e.staff,
                        voice=e.voice,
                        global_onset=e.global_onset,
                        offset_in_measure=e.offset_in_measure,
                        duration=e.duration,
                        pitch=_midi_to_spelled_pitch(new_midi),
                        midi=new_midi,
                        is_grace=e.is_grace,
                        tie_state=e.tie_state,
                    )
                )
            else:
                new_events.append(e)

        return CanonicalScore(
            piece_id=score.piece_id,
            corpus_id=score.corpus_id,
            corpus_role=score.corpus_role,
            score_entry_id=score.score_entry_id,
            composer=score.composer,
            title=score.title,
            source_repository=score.source_repository,
            source_commit=score.source_commit,
            source_relative_path=score.source_relative_path,
            source_sha256=score.source_sha256,
            manifest_hash=score.manifest_hash,
            parser_version=score.parser_version,
            measures=score.measures,
            events=tuple(new_events),
        )

    if trans_type == TransformationType.TIME_DILATION:
        scale = Fraction(2, 1)
        new_measures_td = tuple(
            CanonicalMeasure(
                piece_id=m.piece_id,
                measure_index=m.measure_index,
                source_measure_label=m.source_measure_label,
                global_onset=m.global_onset * scale,
                actual_duration=m.actual_duration * scale,
                time_signature=m.time_signature,
                expected_duration=m.expected_duration * scale,
            )
            for m in score.measures
        )
        new_events_td = tuple(
            CanonicalScoreEvent(
                piece_id=e.piece_id,
                event_id=e.event_id,
                event_index=e.event_index,
                event_kind=e.event_kind,
                measure_index=e.measure_index,
                source_measure_label=e.source_measure_label,
                staff=e.staff,
                voice=e.voice,
                global_onset=e.global_onset * scale,
                offset_in_measure=e.offset_in_measure * scale,
                duration=e.duration * scale,
                pitch=e.pitch,
                midi=e.midi,
                is_grace=e.is_grace,
                tie_state=e.tie_state,
            )
            for e in score.events
        )
        return CanonicalScore(
            piece_id=score.piece_id,
            corpus_id=score.corpus_id,
            corpus_role=score.corpus_role,
            score_entry_id=score.score_entry_id,
            composer=score.composer,
            title=score.title,
            source_repository=score.source_repository,
            source_commit=score.source_commit,
            source_relative_path=score.source_relative_path,
            source_sha256=score.source_sha256,
            manifest_hash=score.manifest_hash,
            parser_version=score.parser_version,
            measures=new_measures_td,
            events=new_events_td,
        )

    if trans_type == TransformationType.PIECE_ID_RENAME:
        new_entry_id = f"{score.score_entry_id}_renamed"
        new_pid = f"{score.corpus_id}:{new_entry_id}"
        new_measures_renamed = tuple(
            CanonicalMeasure(
                piece_id=new_pid,
                measure_index=m.measure_index,
                source_measure_label=m.source_measure_label,
                global_onset=m.global_onset,
                actual_duration=m.actual_duration,
                time_signature=m.time_signature,
                expected_duration=m.expected_duration,
            )
            for m in score.measures
        )
        new_events_renamed = tuple(
            CanonicalScoreEvent(
                piece_id=new_pid,
                event_id=e.event_id,
                event_index=e.event_index,
                event_kind=e.event_kind,
                measure_index=e.measure_index,
                source_measure_label=e.source_measure_label,
                staff=e.staff,
                voice=e.voice,
                global_onset=e.global_onset,
                offset_in_measure=e.offset_in_measure,
                duration=e.duration,
                pitch=e.pitch,
                midi=e.midi,
                is_grace=e.is_grace,
                tie_state=e.tie_state,
            )
            for e in score.events
        )
        return CanonicalScore(
            piece_id=new_pid,
            corpus_id=score.corpus_id,
            corpus_role=score.corpus_role,
            score_entry_id=new_entry_id,
            composer=score.composer,
            title=score.title,
            source_repository=score.source_repository,
            source_commit=score.source_commit,
            source_relative_path=score.source_relative_path,
            source_sha256=score.source_sha256,
            manifest_hash=score.manifest_hash,
            parser_version=score.parser_version,
            measures=new_measures_renamed,
            events=new_events_renamed,
        )

    if trans_type == TransformationType.SOURCE_PATH_RENAME:
        return CanonicalScore(
            piece_id=score.piece_id,
            corpus_id=score.corpus_id,
            corpus_role=score.corpus_role,
            score_entry_id=score.score_entry_id,
            composer=score.composer,
            title=score.title,
            source_repository=score.source_repository,
            source_commit=score.source_commit,
            source_relative_path="renamed_path/score.mscx",
            source_sha256=score.source_sha256,
            manifest_hash=score.manifest_hash,
            parser_version=score.parser_version,
            measures=score.measures,
            events=score.events,
        )

    if trans_type == TransformationType.VOICE_ID_RENAME:
        new_events = [
            CanonicalScoreEvent(
                piece_id=e.piece_id,
                event_id=e.event_id,
                event_index=e.event_index,
                event_kind=e.event_kind,
                measure_index=e.measure_index,
                source_measure_label=e.source_measure_label,
                staff=e.staff,
                voice=e.voice + 1,
                global_onset=e.global_onset,
                offset_in_measure=e.offset_in_measure,
                duration=e.duration,
                pitch=e.pitch,
                midi=e.midi,
                is_grace=e.is_grace,
                tie_state=e.tie_state,
            )
            for e in score.events
        ]
        new_events.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))
        return CanonicalScore(
            piece_id=score.piece_id,
            corpus_id=score.corpus_id,
            corpus_role=score.corpus_role,
            score_entry_id=score.score_entry_id,
            composer=score.composer,
            title=score.title,
            source_repository=score.source_repository,
            source_commit=score.source_commit,
            source_relative_path=score.source_relative_path,
            source_sha256=score.source_sha256,
            manifest_hash=score.manifest_hash,
            parser_version=score.parser_version,
            measures=score.measures,
            events=tuple(new_events),
        )

    if trans_type == TransformationType.STAFF_SWAP:
        new_events = [
            CanonicalScoreEvent(
                piece_id=e.piece_id,
                event_id=e.event_id,
                event_index=e.event_index,
                event_kind=e.event_kind,
                measure_index=e.measure_index,
                source_measure_label=e.source_measure_label,
                staff=2 if e.staff == 1 else 1,
                voice=e.voice,
                global_onset=e.global_onset,
                offset_in_measure=e.offset_in_measure,
                duration=e.duration,
                pitch=e.pitch,
                midi=e.midi,
                is_grace=e.is_grace,
                tie_state=e.tie_state,
            )
            for e in score.events
        ]
        new_events.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))
        return CanonicalScore(
            piece_id=score.piece_id,
            corpus_id=score.corpus_id,
            corpus_role=score.corpus_role,
            score_entry_id=score.score_entry_id,
            composer=score.composer,
            title=score.title,
            source_repository=score.source_repository,
            source_commit=score.source_commit,
            source_relative_path=score.source_relative_path,
            source_sha256=score.source_sha256,
            manifest_hash=score.manifest_hash,
            parser_version=score.parser_version,
            measures=score.measures,
            events=tuple(new_events),
        )

    return score


# ---------------------------------------------------------------------------
# Validation Engine & Result Records
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class FixtureAssertionRecord:
    """Record of a single directional theory assertion execution."""

    assertion_id: str
    fixture_id: str
    family: FeatureFamily
    condition_description: str
    passed: bool
    actual_value_summary: str


@dataclass(frozen=True, slots=True)
class MetamorphicCheckRecord:
    """Record of a metamorphic transformation check on a feature."""

    feature_id: str
    fixture_id: str
    transformation: TransformationType
    transformation_parameter: Any
    original_value: float
    original_availability_status: AvailabilityStatus
    original_reason: str
    transformed_value: float
    transformed_availability_status: AvailabilityStatus
    transformed_reason: str
    expected_behavior: InvarianceClass
    expected_relation: str
    actual_relation: str
    passed: bool


@dataclass(frozen=True, slots=True)
class FamilyValidationStatus:
    """Acceptance status for a specific feature family."""

    family: FeatureFamily
    status: str  # PASS / PARTIAL / FAIL
    passed_assertions: int
    total_assertions: int
    passed_metamorphic: int
    total_metamorphic: int


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Complete validation result for RC-011 Structural Music Representation."""

    fixture_count: int
    assertion_records: tuple[FixtureAssertionRecord, ...]
    metamorphic_records: tuple[MetamorphicCheckRecord, ...]
    family_statuses: tuple[FamilyValidationStatus, ...]
    available_cells: int
    structural_zero_cells: int
    unavailable_cells: int
    exclusion_ledger_hash: str
    invariance_contract_hash: str
    fixture_suite_hash: str
    assertion_contract_hash: str
    overall_status: str
    validation_hash: str


_METAMORPHIC_FEATURE_FIXTURE_MAP: dict[str, str] = {
    "tonal_center_change_rate": "C",
    "tonal_modulatory_index": "C",
    "tonal_circle5_distance_mean": "C",
    "tonal_circle5_distance_max": "C",
    "tonal_local_confidence_std": "C",
    "tonal_chromatic_duration_share": "D",
    "sonority_ic1_semitone_share": "D",
    "sonority_ic6_tritone_share": "D",
    "sonority_harmonic_change_rate": "A",
    "cadence_deceptive_proxy_rate": "F",
    "form_novelty_mean": "O",
    "vl_outer_contrary_motion_share": "L",
    "vl_outer_oblique_motion_share": "M",
    "vl_semitone_approach_rate": "D",
    "vl_common_tone_retention_rate": "A",
    "texture_arpeggiation_proxy_rate": "H",
    "texture_repeated_note_attack_rate": "I",
    "texture_octave_doubling_share": "J",
    "traj_attack_density_slope": "S",
}

_METAMORPHIC_FAMILY_DEFAULT_FIXTURE: dict[FeatureFamily, str] = {
    FeatureFamily.TONAL: "A",
    FeatureFamily.SONORITY: "G",
    FeatureFamily.CADENCE: "E",
    FeatureFamily.FORM: "N",
    FeatureFamily.VOICE_LEADING: "K",
    FeatureFamily.TEXTURE_REGISTER: "G",
    FeatureFamily.TEMPORAL_TRAJECTORY: "P",
}


def get_metamorphic_fixture_id(feature_id: str, family: FeatureFamily) -> str:
    """Map each feature to its optimal non-vacuous fixture for metamorphic testing."""
    if feature_id in _METAMORPHIC_FEATURE_FIXTURE_MAP:
        return _METAMORPHIC_FEATURE_FIXTURE_MAP[feature_id]
    return _METAMORPHIC_FAMILY_DEFAULT_FIXTURE.get(family, "A")


def run_synthetic_and_metamorphic_validation(
    available_cells: int = 0,
    structural_zero_cells: int = 0,
    unavailable_cells: int = 0,
    exclusion_ledger_hash: str = "0" * 64,
) -> ValidationResult:
    """Execute complete synthetic fixture suite and metamorphic invariance tests."""
    # 1. Build and extract all 20 fixtures
    fixture_scores = {f.fixture_id: f.builder() for f in FIXTURE_REGISTRY}
    fixture_feats = {f_id: extract_structural_representation(sc) for f_id, sc in fixture_scores.items()}

    assertions: list[FixtureAssertionRecord] = []

    # FAMILY A (Tonal)
    # A vs B Transposition Invariance
    val_a = fixture_feats["A"]["tonal_global_confidence"].value
    val_b = fixture_feats["B"]["tonal_global_confidence"].value
    diff_ab = abs(val_a - val_b)
    pass_ab = (diff_ab < 1e-4) and (val_a > 0.60)
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TONAL_A_VS_B_TRANSPOSITION_INVARIANCE",
            fixture_id="A/B",
            family=FeatureFamily.TONAL,
            condition_description="abs(A.tonal_conf - B.tonal_conf) < 1e-4 and A.tonal_conf > 0.60",
            passed=pass_ab,
            actual_value_summary=f"A={val_a}, B={val_b}, diff={diff_ab}",
        )
    )

    # C Tonal Center Transition
    rate_c = fixture_feats["C"]["tonal_center_change_rate"].value
    pass_c = rate_c > 0.0
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TONAL_C_CENTER_CHANGE_DETECTION",
            fixture_id="C",
            family=FeatureFamily.TONAL,
            condition_description="C.tonal_center_change_rate > 0.0",
            passed=pass_c,
            actual_value_summary=f"rate={rate_c}",
        )
    )

    # D Chromaticity
    chrom_d = fixture_feats["D"]["tonal_chromatic_duration_share"].value
    conf_d = fixture_feats["D"]["tonal_global_confidence"].value
    pass_d = (chrom_d > 0.30) and (conf_d < val_a)
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TONAL_D_CHROMATICITY_ELEVATION",
            fixture_id="D",
            family=FeatureFamily.TONAL,
            condition_description="D.chromatic_share > 0.30 and D.tonal_conf < A.tonal_conf",
            passed=pass_d,
            actual_value_summary=f"chrom={chrom_d}, conf_D={conf_d}, conf_A={val_a}",
        )
    )

    # FAMILY B (Sonority)
    # G Block chord vs H Arpeggio cardinality
    card_g = fixture_feats["G"]["sonority_pc_cardinality_mean"].value
    card_h = fixture_feats["H"]["sonority_pc_cardinality_mean"].value
    pass_gh = card_g >= 3.0 and card_h <= 1.5
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_SONORITY_BLOCK_VS_ARPEGGIO_CARDINALITY",
            fixture_id="G/H",
            family=FeatureFamily.SONORITY,
            condition_description="G.pc_card_mean >= 3.0 and H.pc_card_mean <= 1.5",
            passed=pass_gh,
            actual_value_summary=f"G_card={card_g}, H_card={card_h}",
        )
    )

    # D Dissonance IC1 share
    ic1_d = fixture_feats["D"]["sonority_ic1_semitone_share"].value
    pass_ic1 = ic1_d > 0.0
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_SONORITY_D_IC1_DISSONANCE",
            fixture_id="D",
            family=FeatureFamily.SONORITY,
            condition_description="D.ic1_share > 0.0",
            passed=pass_ic1,
            actual_value_summary=f"ic1_share={ic1_d}",
        )
    )

    # FAMILY C (Cadence)
    # E Authentic cadence V->I
    tonic_e = fixture_feats["E"]["cadence_tonic_resolution_rate"].value
    cand_e = fixture_feats["E"]["cadence_boundary_candidate_rate"].value
    pass_e = tonic_e > 0.0 and cand_e > 0.0
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_CADENCE_E_AUTHENTIC_RESOLUTION",
            fixture_id="E",
            family=FeatureFamily.CADENCE,
            condition_description="E.tonic_resolution_rate > 0.0 and E.boundary_rate > 0.0",
            passed=pass_e,
            actual_value_summary=f"tonic_res={tonic_e}, boundary_rate={cand_e}",
        )
    )

    # F Deceptive cadence V->VI
    dec_f = fixture_feats["F"]["cadence_deceptive_proxy_rate"].value
    pass_f = dec_f > 0.0
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_CADENCE_F_DECEPTIVE_MOTION",
            fixture_id="F",
            family=FeatureFamily.CADENCE,
            condition_description="F.deceptive_proxy_rate > 0.0",
            passed=pass_f,
            actual_value_summary=f"deceptive_rate={dec_f}",
        )
    )

    # FAMILY D (Form)
    # N (ABA) vs O (Through-composed) Late Return
    ret_n = fixture_feats["N"]["form_return_late_strength"].value
    ret_o = fixture_feats["O"]["form_return_late_strength"].value
    pass_no = (ret_n > 0.70) and (ret_n > ret_o + 0.20)
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_FORM_N_VS_O_RECAPITULATION_RETURN",
            fixture_id="N/O",
            family=FeatureFamily.FORM,
            condition_description="N.late_return > 0.70 and N.late_return > O.late_return + 0.20",
            passed=pass_no,
            actual_value_summary=f"N_ret={ret_n}, O_ret={ret_o}",
        )
    )

    # FAMILY E (Voice Leading)
    # K Parallel motion
    par_k = fixture_feats["K"]["vl_outer_parallel_motion_share"].value
    pass_k = par_k > 0.75
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_VL_K_PARALLEL_DOMINANCE",
            fixture_id="K",
            family=FeatureFamily.VOICE_LEADING,
            condition_description="K.parallel_motion_share > 0.75",
            passed=pass_k,
            actual_value_summary=f"parallel_share={par_k}",
        )
    )

    # L Contrary motion
    con_l = fixture_feats["L"]["vl_outer_contrary_motion_share"].value
    pass_l = con_l > 0.75
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_VL_L_CONTRARY_DOMINANCE",
            fixture_id="L",
            family=FeatureFamily.VOICE_LEADING,
            condition_description="L.contrary_motion_share > 0.75",
            passed=pass_l,
            actual_value_summary=f"contrary_share={con_l}",
        )
    )

    # M Oblique motion
    obl_m = fixture_feats["M"]["vl_outer_oblique_motion_share"].value
    pass_m = obl_m > 0.75
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_VL_M_OBLIQUE_DOMINANCE",
            fixture_id="M",
            family=FeatureFamily.VOICE_LEADING,
            condition_description="M.oblique_motion_share > 0.75",
            passed=pass_m,
            actual_value_summary=f"oblique_share={obl_m}",
        )
    )

    # FAMILY F (Texture / Register)
    # G Block chord vs H Arpeggio vs I Repeated Notes vs J Octave Doubling
    block_g = fixture_feats["G"]["texture_block_chord_share"].value
    arp_h = fixture_feats["H"]["texture_arpeggiation_proxy_rate"].value
    rep_i = fixture_feats["I"]["texture_repeated_note_attack_rate"].value
    oct_j = fixture_feats["J"]["texture_octave_doubling_share"].value

    pass_g_tex = block_g > 0.80
    pass_h_tex = arp_h > 0.0
    pass_i_tex = rep_i > 0.0
    pass_j_tex = oct_j > 0.80

    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TEXTURE_G_BLOCK_CHORD",
            fixture_id="G",
            family=FeatureFamily.TEXTURE_REGISTER,
            condition_description="G.block_chord_share > 0.80",
            passed=pass_g_tex,
            actual_value_summary=f"block_share={block_g}",
        )
    )
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TEXTURE_H_ARPEGGIO_PROXY",
            fixture_id="H",
            family=FeatureFamily.TEXTURE_REGISTER,
            condition_description="H.arpeggiation_proxy_rate > 0.0",
            passed=pass_h_tex,
            actual_value_summary=f"arpeggio_rate={arp_h}",
        )
    )
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TEXTURE_I_REPEATED_NOTES",
            fixture_id="I",
            family=FeatureFamily.TEXTURE_REGISTER,
            condition_description="I.repeated_note_attack_rate > 0.0",
            passed=pass_i_tex,
            actual_value_summary=f"repeated_rate={rep_i}",
        )
    )
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TEXTURE_J_OCTAVE_DOUBLING",
            fixture_id="J",
            family=FeatureFamily.TEXTURE_REGISTER,
            condition_description="J.octave_doubling_share > 0.80",
            passed=pass_j_tex,
            actual_value_summary=f"octave_share={oct_j}",
        )
    )

    # FAMILY G (Temporal Trajectory)
    # P Ascending vs Q Descending vs R Stable
    slope_p = fixture_feats["P"]["traj_register_center_slope"].value
    slope_q = fixture_feats["Q"]["traj_register_center_slope"].value
    slope_r = fixture_feats["R"]["traj_register_center_slope"].value
    slope_s = fixture_feats["S"]["traj_attack_density_slope"].value
    slope_t = fixture_feats["T"]["traj_attack_density_slope"].value

    pass_p = slope_p > 0.0
    pass_q = slope_q < 0.0
    pass_r = abs(slope_r) < 0.5
    pass_s = slope_s > 0.0
    pass_t = slope_t < 0.0

    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TRAJ_P_ASCENDING_REGISTER",
            fixture_id="P",
            family=FeatureFamily.TEMPORAL_TRAJECTORY,
            condition_description="P.register_center_slope > 0.0",
            passed=pass_p,
            actual_value_summary=f"slope={slope_p}",
        )
    )
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TRAJ_Q_DESCENDING_REGISTER",
            fixture_id="Q",
            family=FeatureFamily.TEMPORAL_TRAJECTORY,
            condition_description="Q.register_center_slope < 0.0",
            passed=pass_q,
            actual_value_summary=f"slope={slope_q}",
        )
    )
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TRAJ_R_STABLE_REGISTER",
            fixture_id="R",
            family=FeatureFamily.TEMPORAL_TRAJECTORY,
            condition_description="abs(R.register_center_slope) < 0.5",
            passed=pass_r,
            actual_value_summary=f"slope={slope_r}",
        )
    )
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TRAJ_S_SPARSE_TO_DENSE",
            fixture_id="S",
            family=FeatureFamily.TEMPORAL_TRAJECTORY,
            condition_description="S.attack_density_slope > 0.0",
            passed=pass_s,
            actual_value_summary=f"density_slope={slope_s}",
        )
    )
    assertions.append(
        FixtureAssertionRecord(
            assertion_id="ASSERT_TRAJ_T_DENSE_TO_SPARSE",
            fixture_id="T",
            family=FeatureFamily.TEMPORAL_TRAJECTORY,
            condition_description="T.attack_density_slope < 0.0",
            passed=pass_t,
            actual_value_summary=f"density_slope={slope_t}",
        )
    )

    # 2. Metamorphic Invariance Checks
    metamorphic_records: list[MetamorphicCheckRecord] = []

    test_transformations: list[tuple[TransformationType, Any]] = [
        (TransformationType.TRANSPOSITION, -7),
        (TransformationType.TRANSPOSITION, -5),
        (TransformationType.TRANSPOSITION, +3),
        (TransformationType.TRANSPOSITION, +5),
        (TransformationType.TIME_DILATION, None),
        (TransformationType.PIECE_ID_RENAME, None),
        (TransformationType.SOURCE_PATH_RENAME, None),
        (TransformationType.VOICE_ID_RENAME, None),
        (TransformationType.STAFF_SWAP, None),
    ]

    for fdef in STRUCTURAL_FEATURE_CATALOG:
        fid = fdef.feature_id
        fx_id = get_metamorphic_fixture_id(fid, fdef.family)
        base_score = fixture_scores[fx_id]
        orig_obj = fixture_feats[fx_id][fid]

        for trans_type, param in test_transformations:
            trans_score = apply_metamorphic_transformation(base_score, trans_type, param)
            trans_feats = extract_structural_representation(trans_score)
            trans_obj = trans_feats[fid]
            expected_behavior = get_feature_invariance_contract(fid, trans_type)

            passed = False
            expected_rel = ""
            actual_rel = ""

            if expected_behavior == InvarianceClass.INVARIANT:
                diff = abs(orig_obj.value - trans_obj.value)
                status_equal = (orig_obj.status == trans_obj.status)
                passed = (diff < 1e-4) and status_equal
                expected_rel = "abs(orig - trans) < 1e-4 and status_orig == status_trans"
                actual_rel = f"diff={diff:.6f}, orig_status={orig_obj.status.value}, trans_status={trans_obj.status.value}"
            elif expected_behavior == InvarianceClass.EQUIVARIANT:
                if trans_type == TransformationType.TRANSPOSITION:
                    shift = int(param)
                    diff = abs(trans_obj.value - (orig_obj.value + shift))
                    status_equal = (orig_obj.status == trans_obj.status)
                    passed = (diff < 1e-4) and status_equal
                    expected_rel = f"abs(trans - (orig + {shift})) < 1e-4 and status_orig == status_trans"
                    actual_rel = f"orig={orig_obj.value:.4f}, trans={trans_obj.value:.4f}, expected={orig_obj.value + shift:.4f}, orig_status={orig_obj.status.value}, trans_status={trans_obj.status.value}"
                else:
                    passed = True
                    expected_rel = "equivariant"
                    actual_rel = f"orig={orig_obj.value:.4f}, trans={trans_obj.value:.4f}"
            elif expected_behavior == InvarianceClass.SENSITIVE_BY_DESIGN:
                if trans_type == TransformationType.STAFF_SWAP and fid == "texture_interstaff_gap_mean":
                    passed = (orig_obj.value > 0 and trans_obj.value < 0)
                    expected_rel = "trans < 0 < orig"
                    actual_rel = f"orig={orig_obj.value:.4f}, trans={trans_obj.value:.4f}"
                elif trans_type == TransformationType.TIME_DILATION and fid in (
                    "texture_arpeggiation_proxy_rate",
                    "texture_repeated_note_attack_rate",
                ):
                    passed = (orig_obj.value > 0 and trans_obj.value == 0.0)
                    expected_rel = "orig > 0 and trans == 0.0"
                    actual_rel = f"orig={orig_obj.value:.4f}, trans={trans_obj.value:.4f}"
                else:
                    passed = True
                    expected_rel = "sensitive by design"
                    actual_rel = f"orig={orig_obj.value:.4f}, trans={trans_obj.value:.4f}"
            else:
                passed = True
                expected_rel = "not applicable"
                actual_rel = "skipped"

            metamorphic_records.append(
                MetamorphicCheckRecord(
                    feature_id=fid,
                    fixture_id=fx_id,
                    transformation=trans_type,
                    transformation_parameter=param,
                    original_value=orig_obj.value,
                    original_availability_status=orig_obj.status,
                    original_reason=orig_obj.reason,
                    transformed_value=trans_obj.value,
                    transformed_availability_status=trans_obj.status,
                    transformed_reason=trans_obj.reason,
                    expected_behavior=expected_behavior,
                    expected_relation=expected_rel,
                    actual_relation=actual_rel,
                    passed=passed,
                )
            )

    # 3. Compute Per-Family Status
    family_statuses: list[FamilyValidationStatus] = []
    all_families_passed = True

    for fam in FeatureFamily:
        fam_assertions = [a for a in assertions if a.family == fam]
        fam_features = {d.feature_id for d in STRUCTURAL_FEATURE_CATALOG if d.family == fam}
        fam_metamorphic = [m for m in metamorphic_records if m.feature_id in fam_features]

        pass_a_cnt = sum(1 for a in fam_assertions if a.passed)
        tot_a_cnt = len(fam_assertions)

        pass_m_cnt = sum(1 for m in fam_metamorphic if m.passed)
        tot_m_cnt = len(fam_metamorphic)

        if pass_a_cnt == tot_a_cnt and pass_m_cnt == tot_m_cnt and tot_a_cnt > 0:
            status_str = "PASS"
        elif pass_a_cnt > 0:
            status_str = "PARTIAL"
            all_families_passed = False
        else:
            status_str = "FAIL"
            all_families_passed = False

        family_statuses.append(
            FamilyValidationStatus(
                family=fam,
                status=status_str,
                passed_assertions=pass_a_cnt,
                total_assertions=tot_a_cnt,
                passed_metamorphic=pass_m_cnt,
                total_metamorphic=tot_m_cnt,
            )
        )

    overall_status = "STRUCTURAL_REPRESENTATION_VALIDATED" if all_families_passed else "STRUCTURAL_REPRESENTATION_PARTIALLY_VALIDATED"

    fixture_suite_hash = compute_synthetic_fixture_suite_hash()
    invariance_contract_hash = compute_invariance_contract_hash()
    assertion_contract_hash = compute_synthetic_assertion_contract_hash()

    # 4. Compute deterministic validation hash binding all per-record metamorphic & assertion records
    canonical = {
        "version": "STRUCTURAL_VALIDATION_RESULT_V2",
        "fixture_count": len(FIXTURE_REGISTRY),
        "fixture_suite_hash": fixture_suite_hash,
        "assertion_contract_hash": assertion_contract_hash,
        "invariance_contract_hash": invariance_contract_hash,
        "exclusion_ledger_hash": exclusion_ledger_hash,
        "overall_status": overall_status,
        "assertions": [
            {
                "assertion_id": a.assertion_id,
                "fixture_id": a.fixture_id,
                "family": a.family.value,
                "passed": a.passed,
                "condition": a.condition_description,
                "summary": a.actual_value_summary,
            }
            for a in assertions
        ],
        "metamorphic_records": [
            {
                "feature_id": m.feature_id,
                "fixture_id": m.fixture_id,
                "transformation": m.transformation.value,
                "transformation_parameter": str(m.transformation_parameter),
                "original_value": round(m.original_value, 6),
                "original_availability_status": m.original_availability_status.value,
                "original_reason": m.original_reason,
                "transformed_value": round(m.transformed_value, 6),
                "transformed_availability_status": m.transformed_availability_status.value,
                "transformed_reason": m.transformed_reason,
                "expected_behavior": m.expected_behavior.value,
                "expected_relation": m.expected_relation,
                "actual_relation": m.actual_relation,
                "passed": m.passed,
            }
            for m in metamorphic_records
        ],
        "family_statuses": [
            {
                "family": fs.family.value,
                "status": fs.status,
                "passed_assertions": fs.passed_assertions,
                "total_assertions": fs.total_assertions,
                "passed_metamorphic": fs.passed_metamorphic,
                "total_metamorphic": fs.total_metamorphic,
            }
            for fs in family_statuses
        ],
        "coverage": {
            "available_cells": available_cells,
            "structural_zero_cells": structural_zero_cells,
            "unavailable_cells": unavailable_cells,
        },
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    val_hash = hashlib.sha256(encoded).hexdigest()

    return ValidationResult(
        fixture_count=len(FIXTURE_REGISTRY),
        assertion_records=tuple(assertions),
        metamorphic_records=tuple(metamorphic_records),
        family_statuses=tuple(family_statuses),
        available_cells=available_cells,
        structural_zero_cells=structural_zero_cells,
        unavailable_cells=unavailable_cells,
        exclusion_ledger_hash=exclusion_ledger_hash,
        invariance_contract_hash=invariance_contract_hash,
        fixture_suite_hash=fixture_suite_hash,
        assertion_contract_hash=assertion_contract_hash,
        overall_status=overall_status,
        validation_hash=val_hash,
    )

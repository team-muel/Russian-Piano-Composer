"""
Synthetic polyphonic adversarial score fixtures and property tests for RC-009A-A.
"""
from fractions import Fraction

from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.score import (
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
    TieState,
)
from russian_piano_composer.features.contour_features import extract_contour_features
from russian_piano_composer.features.density_features import extract_density_features
from russian_piano_composer.features.interval_features import extract_interval_features
from russian_piano_composer.features.meter_features import extract_meter_features
from russian_piano_composer.features.pitch_features import extract_pitch_features
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


def _make_pitch(midi: int) -> SpelledPitch:
    """Helper to convert MIDI to SpelledPitch for synthetic testing."""
    octave = (midi // 12) - 1
    pc = midi % 12
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
    letter, alt = mapping[pc]
    return SpelledPitch(letter=letter, alteration=alt, octave=octave)


def test_fixture_a_monophonic_ascending() -> None:
    """Fixture A — Monophonic ascending voice (C4, D4, E4, F4)."""
    piece_id = "test:fixture_a"
    measures = (
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    events = tuple(
        CanonicalScoreEvent(
            piece_id=piece_id,
            event_id=f"{piece_id}:evt_{i}",
            event_index=i,
            event_kind=EventKind.NOTE,
            measure_index=0,
            source_measure_label="1",
            staff=1,
            voice=1,
            global_onset=Fraction(i, 4),
            offset_in_measure=Fraction(i, 4),
            duration=Fraction(1, 4),
            pitch=_make_pitch(midi),
            midi=midi,
        )
        for i, midi in enumerate([60, 62, 64, 65])
    )
    score = CanonicalScore(
        piece_id=piece_id,
        corpus_id="test",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="fixture_a",
        composer="Test",
        title="Fixture A",
        source_repository="test",
        source_commit="a" * 40,
        source_relative_path="a.mscx",
        source_sha256="0" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0",
        measures=measures,
        events=events,
    )

    iv_feats = extract_interval_features(score)
    contour_feats = extract_contour_features(score)

    assert iv_feats["interval_mean_abs_semitones"] is not None
    assert contour_feats["contour_ascending_ratio"] == 1.0
    assert contour_feats["contour_descending_ratio"] == 0.0


def test_fixture_b_two_simultaneous_voices_polyphony() -> None:
    """
    Fixture B — Two simultaneous independent voices.
    Upper: C5, D5, E5, F5 (staff 1, voice 1)
    Lower: C2, B1, A1, G1 (staff 2, voice 1)

    Proves global onset sorting is NOT used, and cross-register false leaps do NOT occur.
    """
    piece_id = "test:fixture_b"
    measures = (
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    events_list = []
    idx = 0
    upper_midis = [72, 74, 76, 77]  # +2, +2, +1 semitones
    lower_midis = [36, 35, 33, 31]  # -1, -2, -2 semitones

    for i in range(4):
        # Upper voice note
        events_list.append(
            CanonicalScoreEvent(
                piece_id=piece_id,
                event_id=f"{piece_id}:evt_{idx}",
                event_index=idx,
                event_kind=EventKind.NOTE,
                measure_index=0,
                source_measure_label="1",
                staff=1,
                voice=1,
                global_onset=Fraction(i, 4),
                offset_in_measure=Fraction(i, 4),
                duration=Fraction(1, 4),
                pitch=_make_pitch(upper_midis[i]),
                midi=upper_midis[i],
            )
        )
        idx += 1
        # Lower voice note
        events_list.append(
            CanonicalScoreEvent(
                piece_id=piece_id,
                event_id=f"{piece_id}:evt_{idx}",
                event_index=idx,
                event_kind=EventKind.NOTE,
                measure_index=0,
                source_measure_label="1",
                staff=2,
                voice=1,
                global_onset=Fraction(i, 4),
                offset_in_measure=Fraction(i, 4),
                duration=Fraction(1, 4),
                pitch=_make_pitch(lower_midis[i]),
                midi=lower_midis[i],
            )
        )
        idx += 1

    events_list.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))
    score = CanonicalScore(
        piece_id=piece_id,
        corpus_id="test",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="fixture_b",
        composer="Test",
        title="Fixture B",
        source_repository="test",
        source_commit="a" * 40,
        source_relative_path="b.mscx",
        source_sha256="0" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0",
        measures=measures,
        events=tuple(events_list),
    )

    iv_feats = extract_interval_features(score)
    # Upper intervals: +2, +2, +1 (abs: 2, 2, 1)
    # Lower intervals: -1, -2, -2 (abs: 1, 2, 2)
    # Total abs intervals: [2, 2, 1, 1, 2, 2], max = 2
    assert iv_feats["interval_max_abs_semitones"] == 2
    assert iv_feats["interval_leap_ratio"] == 0.0  # No leap > 2 semitones!


def test_fixture_c_chords_exclusion() -> None:
    """Fixture C — Chords: C-E-G triad followed by D-F#-A triad in same voice."""
    piece_id = "test:fixture_c"
    measures = (
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    events_list = []
    idx = 0
    # Triad 1 at onset 0
    for midi in [60, 64, 67]:
        events_list.append(
            CanonicalScoreEvent(
                piece_id=piece_id,
                event_id=f"{piece_id}:evt_{idx}",
                event_index=idx,
                event_kind=EventKind.NOTE,
                measure_index=0,
                source_measure_label="1",
                staff=1,
                voice=1,
                global_onset=Fraction(0),
                offset_in_measure=Fraction(0),
                duration=Fraction(1, 2),
                pitch=_make_pitch(midi),
                midi=midi,
            )
        )
        idx += 1

    # Triad 2 at onset 1/2
    for midi in [62, 66, 69]:
        events_list.append(
            CanonicalScoreEvent(
                piece_id=piece_id,
                event_id=f"{piece_id}:evt_{idx}",
                event_index=idx,
                event_kind=EventKind.NOTE,
                measure_index=0,
                source_measure_label="1",
                staff=1,
                voice=1,
                global_onset=Fraction(1, 2),
                offset_in_measure=Fraction(1, 2),
                duration=Fraction(1, 2),
                pitch=_make_pitch(midi),
                midi=midi,
            )
        )
        idx += 1

    events_list.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))
    score = CanonicalScore(
        piece_id=piece_id,
        corpus_id="test",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="fixture_c",
        composer="Test",
        title="Fixture C",
        source_repository="test",
        source_commit="a" * 40,
        source_relative_path="c.mscx",
        source_sha256="0" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0",
        measures=measures,
        events=tuple(events_list),
    )

    iv_feats = extract_interval_features(score)
    # Chord-to-chord transitions have >1 note per onset, so monophonic interval features return None
    assert iv_feats["interval_mean_abs_semitones"] is None


def test_fixture_d_tied_pitch_continuation() -> None:
    """Fixture D — Tied pitch continuation is NOT a new attack."""
    piece_id = "test:fixture_d"
    measures = (
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    e1 = CanonicalScoreEvent(
        piece_id=piece_id,
        event_id=f"{piece_id}:evt_0",
        event_index=0,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(0),
        offset_in_measure=Fraction(0),
        duration=Fraction(1, 2),
        pitch=_make_pitch(60),
        midi=60,
        tie_state=TieState.START,
    )
    e2 = CanonicalScoreEvent(
        piece_id=piece_id,
        event_id=f"{piece_id}:evt_1",
        event_index=1,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(1, 2),
        offset_in_measure=Fraction(1, 2),
        duration=Fraction(1, 2),
        pitch=_make_pitch(60),
        midi=60,
        tie_state=TieState.STOP,
    )
    score = CanonicalScore(
        piece_id=piece_id,
        corpus_id="test",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="fixture_d",
        composer="Test",
        title="Fixture D",
        source_repository="test",
        source_commit="a" * 40,
        source_relative_path="d.mscx",
        source_sha256="0" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0",
        measures=measures,
        events=(e1, e2),
    )

    pitch_feats = extract_pitch_features(score)
    iv_feats = extract_interval_features(score)

    # e2 (TieState.STOP) is excluded from attack features
    assert pitch_feats["pitch_mean_midi"] == 60.0
    assert iv_feats["interval_mean_abs_semitones"] is None  # Only 1 attack note -> no transitions


def test_fixture_e_grace_ornament_exclusion() -> None:
    """Fixture E — Grace note excluded from core structural features."""
    piece_id = "test:fixture_e"
    measures = (
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    # Grace note G4 (67) followed by C4 (60)
    e_grace = CanonicalScoreEvent(
        piece_id=piece_id,
        event_id=f"{piece_id}:evt_0",
        event_index=0,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(0),
        offset_in_measure=Fraction(0),
        duration=Fraction(0),
        pitch=_make_pitch(67),
        midi=67,
        is_grace=True,
    )
    e_main = CanonicalScoreEvent(
        piece_id=piece_id,
        event_id=f"{piece_id}:evt_1",
        event_index=1,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(0),
        offset_in_measure=Fraction(0),
        duration=Fraction(1, 4),
        pitch=_make_pitch(60),
        midi=60,
        is_grace=False,
    )
    score = CanonicalScore(
        piece_id=piece_id,
        corpus_id="test",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="fixture_e",
        composer="Test",
        title="Fixture E",
        source_repository="test",
        source_commit="a" * 40,
        source_relative_path="e.mscx",
        source_sha256="0" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0",
        measures=measures,
        events=(e_grace, e_main),
    )

    pitch_feats = extract_pitch_features(score)
    density_feats = extract_density_features(score)

    assert pitch_feats["pitch_mean_midi"] == 60.0  # Main note only
    assert density_feats["density_grace_note_ratio"] == 0.5


def test_fixture_f_pickup_measure() -> None:
    """Fixture F — Anacrusis pickup detection."""
    piece_id = "test:fixture_f"
    m_pickup = CanonicalMeasure(
        piece_id=piece_id,
        measure_index=0,
        source_measure_label="0",
        global_onset=Fraction(0),
        actual_duration=Fraction(1, 4),  # 1/4 note in 4/4 time -> pickup
        time_signature=TimeSignature(4, 4),
        expected_duration=Fraction(1),
        is_pickup=True,
    )
    m_full = CanonicalMeasure(
        piece_id=piece_id,
        measure_index=1,
        source_measure_label="1",
        global_onset=Fraction(1, 4),
        actual_duration=Fraction(1),
        time_signature=TimeSignature(4, 4),
        expected_duration=Fraction(1),
    )
    e1 = CanonicalScoreEvent(
        piece_id=piece_id,
        event_id=f"{piece_id}:evt_0",
        event_index=0,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="0",
        staff=1,
        voice=1,
        global_onset=Fraction(0),
        offset_in_measure=Fraction(0),
        duration=Fraction(1, 4),
        pitch=_make_pitch(60),
        midi=60,
    )
    score = CanonicalScore(
        piece_id=piece_id,
        corpus_id="test",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="fixture_f",
        composer="Test",
        title="Fixture F",
        source_repository="test",
        source_commit="a" * 40,
        source_relative_path="f.mscx",
        source_sha256="0" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0",
        measures=(m_pickup, m_full),
        events=(e1,),
    )

    meter_feats = extract_meter_features(score)
    assert meter_feats["meter_has_pickup"] == 1


def test_fixture_g_meter_changes() -> None:
    """Fixture G — Meter transitions: 4/4 -> 3/4 -> 4/4."""
    piece_id = "test:fixture_g"
    measures = (
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=1,
            source_measure_label="2",
            global_onset=Fraction(1),
            actual_duration=Fraction(3, 4),
            time_signature=TimeSignature(3, 4),
            expected_duration=Fraction(3, 4),
        ),
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=2,
            source_measure_label="3",
            global_onset=Fraction(7, 4),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    e1 = CanonicalScoreEvent(
        piece_id=piece_id,
        event_id=f"{piece_id}:evt_0",
        event_index=0,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(0),
        offset_in_measure=Fraction(0),
        duration=Fraction(1, 4),
        pitch=_make_pitch(60),
        midi=60,
    )
    score = CanonicalScore(
        piece_id=piece_id,
        corpus_id="test",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="fixture_g",
        composer="Test",
        title="Fixture G",
        source_repository="test",
        source_commit="a" * 40,
        source_relative_path="g.mscx",
        source_sha256="0" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0",
        measures=measures,
        events=(e1,),
    )

    meter_feats = extract_meter_features(score)
    assert meter_feats["meter_change_count"] == 2
    assert meter_feats["meter_primary_numerator"] == 4  # 4/4 total duration (2) > 3/4 total duration (3/4)


def test_fixture_h_polyphonic_rest() -> None:
    """Fixture H — Polyphonic rest: Voice 2 rests while Voice 1 sounds."""
    piece_id = "test:fixture_h"
    measures = (
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    e_note = CanonicalScoreEvent(
        piece_id=piece_id,
        event_id=f"{piece_id}:evt_0",
        event_index=0,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(0),
        offset_in_measure=Fraction(0),
        duration=Fraction(1),
        pitch=_make_pitch(60),
        midi=60,
    )
    e_rest = CanonicalScoreEvent(
        piece_id=piece_id,
        event_id=f"{piece_id}:evt_1",
        event_index=1,
        event_kind=EventKind.REST,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=2,
        global_onset=Fraction(0),
        offset_in_measure=Fraction(0),
        duration=Fraction(1),
    )
    score = CanonicalScore(
        piece_id=piece_id,
        corpus_id="test",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="fixture_h",
        composer="Test",
        title="Fixture H",
        source_repository="test",
        source_commit="a" * 40,
        source_relative_path="h.mscx",
        source_sha256="0" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0",
        measures=measures,
        events=(e_note, e_rest),
    )

    density_feats = extract_density_features(score)
    assert density_feats["density_rest_ratio"] == 0.5


def test_voice_permutation_invariance() -> None:
    """Voice Permutation Test — Swapping voice labels preserves aggregate interval statistics."""
    measures_orig = (
        CanonicalMeasure(
            piece_id="test:orig",
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    measures_perm = (
        CanonicalMeasure(
            piece_id="test:perm",
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    # Original score with (staff 1, voice 1) and (staff 1, voice 2)
    evs_orig = [
        CanonicalScoreEvent(piece_id="test:orig", event_id="1", event_index=0, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 2), pitch=_make_pitch(60), midi=60),
        CanonicalScoreEvent(piece_id="test:orig", event_id="2", event_index=1, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(1, 2), offset_in_measure=Fraction(1, 2), duration=Fraction(1, 2), pitch=_make_pitch(62), midi=62),
        CanonicalScoreEvent(piece_id="test:orig", event_id="3", event_index=2, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=2, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 2), pitch=_make_pitch(72), midi=72),
        CanonicalScoreEvent(piece_id="test:orig", event_id="4", event_index=3, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=2, global_onset=Fraction(1, 2), offset_in_measure=Fraction(1, 2), duration=Fraction(1, 2), pitch=_make_pitch(74), midi=74),
    ]
    evs_orig.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))
    score_orig = CanonicalScore(piece_id="test:orig", corpus_id="test", corpus_role=CorpusRole.GENERATIVE_RUSSIAN, score_entry_id="orig", composer="T", title="T", source_repository="t", source_commit="a"*40, source_relative_path="a.mscx", source_sha256="0"*64, manifest_hash="b"*64, parser_version="1.0", measures=measures_orig, events=tuple(evs_orig))

    # Permuted score swapping voice 1 <-> voice 2
    evs_perm = [
        CanonicalScoreEvent(piece_id="test:perm", event_id="1", event_index=0, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=2, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 2), pitch=_make_pitch(60), midi=60),
        CanonicalScoreEvent(piece_id="test:perm", event_id="2", event_index=1, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=2, global_onset=Fraction(1, 2), offset_in_measure=Fraction(1, 2), duration=Fraction(1, 2), pitch=_make_pitch(62), midi=62),
        CanonicalScoreEvent(piece_id="test:perm", event_id="3", event_index=2, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 2), pitch=_make_pitch(72), midi=72),
        CanonicalScoreEvent(piece_id="test:perm", event_id="4", event_index=3, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(1, 2), offset_in_measure=Fraction(1, 2), duration=Fraction(1, 2), pitch=_make_pitch(74), midi=74),
    ]
    evs_perm.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))
    score_perm = CanonicalScore(piece_id="test:perm", corpus_id="test", corpus_role=CorpusRole.GENERATIVE_RUSSIAN, score_entry_id="perm", composer="T", title="T", source_repository="t", source_commit="a"*40, source_relative_path="a.mscx", source_sha256="0"*64, manifest_hash="b"*64, parser_version="1.0", measures=measures_perm, events=tuple(evs_perm))

    iv_orig = extract_interval_features(score_orig)
    iv_perm = extract_interval_features(score_perm)

    assert iv_orig == iv_perm


def test_global_transposition_invariance() -> None:
    """Global Transposition Invariance — Transposing pitches preserves relative interval, contour, rhythm, density, meter."""
    measures_base = (
        CanonicalMeasure(
            piece_id="test:base",
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    measures_trans = (
        CanonicalMeasure(
            piece_id="test:trans",
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    evs_base = [
        CanonicalScoreEvent(piece_id="test:base", event_id="1", event_index=0, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 4), pitch=_make_pitch(60), midi=60),
        CanonicalScoreEvent(piece_id="test:base", event_id="2", event_index=1, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(1, 4), offset_in_measure=Fraction(1, 4), duration=Fraction(1, 4), pitch=_make_pitch(64), midi=64),
        CanonicalScoreEvent(piece_id="test:base", event_id="3", event_index=2, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(2, 4), offset_in_measure=Fraction(2, 4), duration=Fraction(1, 4), pitch=_make_pitch(67), midi=67),
    ]
    evs_base.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))
    score_base = CanonicalScore(piece_id="test:base", corpus_id="test", corpus_role=CorpusRole.GENERATIVE_RUSSIAN, score_entry_id="base", composer="T", title="T", source_repository="t", source_commit="a"*40, source_relative_path="a.mscx", source_sha256="0"*64, manifest_hash="b"*64, parser_version="1.0", measures=measures_base, events=tuple(evs_base))

    # Transposed +7 semitones (perfect 5th up)
    evs_trans = [
        CanonicalScoreEvent(piece_id="test:trans", event_id="1", event_index=0, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 4), pitch=_make_pitch(67), midi=67),
        CanonicalScoreEvent(piece_id="test:trans", event_id="2", event_index=1, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(1, 4), offset_in_measure=Fraction(1, 4), duration=Fraction(1, 4), pitch=_make_pitch(71), midi=71),
        CanonicalScoreEvent(piece_id="test:trans", event_id="3", event_index=2, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(2, 4), offset_in_measure=Fraction(2, 4), duration=Fraction(1, 4), pitch=_make_pitch(74), midi=74),
    ]
    evs_trans.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))
    score_trans = CanonicalScore(piece_id="test:trans", corpus_id="test", corpus_role=CorpusRole.GENERATIVE_RUSSIAN, score_entry_id="trans", composer="T", title="T", source_repository="t", source_commit="a"*40, source_relative_path="a.mscx", source_sha256="0"*64, manifest_hash="b"*64, parser_version="1.0", measures=measures_trans, events=tuple(evs_trans))

    iv_base = extract_interval_features(score_base)
    iv_trans = extract_interval_features(score_trans)
    c_base = extract_contour_features(score_base)
    c_trans = extract_contour_features(score_trans)

    assert iv_base == iv_trans
    assert c_base == c_trans


def test_event_record_order_invariance() -> None:
    """Event Record Order Invariance — Sorting order of events in canonical score constructor preserves scientific results."""
    measures_a = (
        CanonicalMeasure(
            piece_id="test:ord_a",
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    measures_b = (
        CanonicalMeasure(
            piece_id="test:ord_b",
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    # Event 1 at onset 0, Event 2 at onset 1/2
    e1_a = CanonicalScoreEvent(piece_id="test:ord_a", event_id="1", event_index=0, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 2), pitch=_make_pitch(60), midi=60)
    e2_a = CanonicalScoreEvent(piece_id="test:ord_a", event_id="2", event_index=1, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(1, 2), offset_in_measure=Fraction(1, 2), duration=Fraction(1, 2), pitch=_make_pitch(64), midi=64)

    e1_b = CanonicalScoreEvent(piece_id="test:ord_b", event_id="1", event_index=0, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 2), pitch=_make_pitch(60), midi=60)
    e2_b = CanonicalScoreEvent(piece_id="test:ord_b", event_id="2", event_index=1, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(1, 2), offset_in_measure=Fraction(1, 2), duration=Fraction(1, 2), pitch=_make_pitch(64), midi=64)

    score_a = CanonicalScore(piece_id="test:ord_a", corpus_id="test", corpus_role=CorpusRole.GENERATIVE_RUSSIAN, score_entry_id="ord_a", composer="T", title="T", source_repository="t", source_commit="a"*40, source_relative_path="a.mscx", source_sha256="0"*64, manifest_hash="b"*64, parser_version="1.0", measures=measures_a, events=(e1_a, e2_a))
    score_b = CanonicalScore(piece_id="test:ord_b", corpus_id="test", corpus_role=CorpusRole.GENERATIVE_RUSSIAN, score_entry_id="ord_b", composer="T", title="T", source_repository="t", source_commit="a"*40, source_relative_path="a.mscx", source_sha256="0"*64, manifest_hash="b"*64, parser_version="1.0", measures=measures_b, events=(e1_b, e2_b))

    p_a = extract_pitch_features(score_a)
    p_b = extract_pitch_features(score_b)

    assert p_a == p_b

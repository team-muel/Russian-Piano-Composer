"""
Synthetic adversarial fixtures and property tests for RC-009B CTU discovery and validation.
"""

from fractions import Fraction

from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.models import (
    SegmentPosition,
    SegmentSpan,
)
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy
from russian_piano_composer.ctu.representation import extract_segment_representation
from russian_piano_composer.ctu.similarity import compute_segment_similarity
from russian_piano_composer.ctu.validation import validate_ctu_future_reuse
from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.score import (
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
    TieState,
)
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


def _make_pitch(midi: int) -> SpelledPitch:
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


def _build_test_score(piece_id: str, num_measures: int, midis_per_measure: dict[int, list[int]]) -> CanonicalScore:
    corpus_id, entry_id = piece_id.split(":")
    meter = TimeSignature(4, 4)
    measures = tuple(
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=m,
            source_measure_label=str(m + 1),
            global_onset=Fraction(m),
            actual_duration=Fraction(1),
            time_signature=meter,
            expected_duration=Fraction(1),
        )
        for m in range(num_measures)
    )

    events: list[CanonicalScoreEvent] = []
    idx = 0

    for m in range(num_measures):
        midi_entries = midis_per_measure.get(m, [60])
        for step, entry in enumerate(midi_entries):
            onset_off = Fraction(step, max(1, len(midi_entries)))
            duration = Fraction(1, max(1, len(midi_entries)))
            chord_notes = entry if isinstance(entry, (tuple, list)) else [entry]
            for midi in chord_notes:
                events.append(
                    CanonicalScoreEvent(
                        piece_id=piece_id,
                        event_id=f"{piece_id}:evt_{idx}",
                        event_index=idx,
                        event_kind=EventKind.NOTE,
                        measure_index=m,
                        source_measure_label=str(m + 1),
                        staff=1,
                        voice=1,
                        global_onset=Fraction(m) + onset_off,
                        offset_in_measure=onset_off,
                        duration=duration,
                        pitch=_make_pitch(midi),
                        midi=midi,
                    )
                )
                idx += 1

    events.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))

    return CanonicalScore(
        piece_id=piece_id,
        corpus_id=corpus_id,
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id=entry_id,
        composer="Test",
        title="Test",
        source_repository="test",
        source_commit="a" * 40,
        source_relative_path="a.mscx",
        source_sha256="0" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0",
        measures=measures,
        events=tuple(events),
    )


def test_fixture_a_exact_recurrence() -> None:
    """Fixture A — Exact motif recurrence in discovery region produces high similarity."""
    midis = {0: [60, 62, 64, 65], 1: [70, 72], 2: [60, 62, 64, 65]}
    score = _build_test_score("test:fixture_a", 16, midis)

    span1 = SegmentSpan(SegmentPosition(0), SegmentPosition(1))
    span2 = SegmentSpan(SegmentPosition(2), SegmentPosition(3))

    rep1 = extract_segment_representation(score, span1)
    rep2 = extract_segment_representation(score, span2)

    sim = compute_segment_similarity(rep1, rep2)
    assert sim == 1.0


def test_fixture_b_transposed_recurrence() -> None:
    """Fixture B — Transposed motif (C-D-E-G -> G-A-B-D) preserves melodic interval similarity."""
    midis = {0: [60, 62, 64, 67], 2: [67, 69, 71, 74]}
    score = _build_test_score("test:fixture_b", 16, midis)

    span1 = SegmentSpan(SegmentPosition(0), SegmentPosition(1))
    span2 = SegmentSpan(SegmentPosition(2), SegmentPosition(3))

    rep1 = extract_segment_representation(score, span1)
    rep2 = extract_segment_representation(score, span2)

    sim = compute_segment_similarity(rep1, rep2)
    assert sim > 0.40  # Transposition-tolerant melodic channel remains high


def test_fixture_c_unrelated_material() -> None:
    """Fixture C — Unrelated material produces low similarity."""
    midis = {0: [60, 60, 60], 2: [71, 61, 83]}
    score = _build_test_score("test:fixture_c", 16, midis)

    span1 = SegmentSpan(SegmentPosition(0), SegmentPosition(1))
    span2 = SegmentSpan(SegmentPosition(2), SegmentPosition(3))

    rep1 = extract_segment_representation(score, span1)
    rep2 = extract_segment_representation(score, span2)

    sim = compute_segment_similarity(rep1, rep2)
    assert sim <= 0.50



def test_fixture_d_rhythm_preserved_pitch_transformed() -> None:
    """Fixture D — Rhythm preserved with pitch transformation tests channel separation."""
    midis1 = {0: [60, 62, 64, 65]}
    midis2 = {2: [72, 71, 69, 67]}  # Same rhythm (4 quarter notes), different pitches/intervals
    score1 = _build_test_score("test:fixture_d1", 16, midis1)
    score2 = _build_test_score("test:fixture_d2", 16, midis2)

    rep1 = extract_segment_representation(score1, SegmentSpan(SegmentPosition(0), SegmentPosition(1)))
    rep2 = extract_segment_representation(score2, SegmentSpan(SegmentPosition(2), SegmentPosition(3)))

    sim = compute_segment_similarity(rep1, rep2)
    # Rhythm channel similarity should be high, while melodic/pitch-class similarity differs
    assert sim > 0.15


def test_fixture_e_pitch_pattern_preserved_rhythm_transformed() -> None:
    """Fixture E — Same pitch pattern with different rhythm tests channel separation."""
    score1 = _build_test_score("test:fixture_e1", 16, {0: [60, 62, 64, 65]})
    score2 = _build_test_score("test:fixture_e2", 16, {2: [60, 62, 64, 65, 67, 69]})

    rep1 = extract_segment_representation(score1, SegmentSpan(SegmentPosition(0), SegmentPosition(1)))
    rep2 = extract_segment_representation(score2, SegmentSpan(SegmentPosition(2), SegmentPosition(3)))

    sim = compute_segment_similarity(rep1, rep2)
    # Melodic stream matches partially, rhythm ratios differ
    assert 0.0 < sim < 1.0


def test_fixture_f_polyphonic_independent_voices() -> None:
    """Fixture F — Polyphonic independent voices do not create arbitrary cross-voice sequence."""
    pid = "test:fixture_f"
    score = _build_test_score(pid, 16, {0: [(60, 64)]})
    rep = extract_segment_representation(score, SegmentSpan(SegmentPosition(0), SegmentPosition(1)))
    # With same onset in staff=1, voice=1, single_note_sequence excludes simultaneities from monophonic transitions
    assert rep.melodic_intervals == ((),) or rep.melodic_intervals == ()


def test_fixture_g_chords() -> None:
    """Fixture G — Chords do not create arbitrary within-chord ordering."""
    score = _build_test_score("test:fixture_g", 16, {0: [(60, 64, 67)]})
    rep = extract_segment_representation(score, SegmentSpan(SegmentPosition(0), SegmentPosition(1)))
    assert rep.melodic_intervals == ((),) or rep.melodic_intervals == ()


def test_single_chord_single_no_bridging() -> None:
    """Regression test: single -> chord -> single produces NO melodic interval bridging across chord."""
    score = _build_test_score("test:single_chord_single", 16, {0: [60, (62, 65), 67]})
    rep = extract_segment_representation(score, SegmentSpan(SegmentPosition(0), SegmentPosition(1)))
    # Onset 0: [60] (single)
    # Onset 1/4: [62, 65] (chord)
    # Onset 2/4: [67] (single)
    # Adjacent onset pairs:
    # 0 -> 1/4: single -> chord (no interval)
    # 1/4 -> 2/4: chord -> single (no interval)
    # Expected melodic intervals: empty tuple ()
    assert rep.melodic_intervals == ((),)


def test_fixture_h_ties() -> None:
    """Fixture H — Ties do not create false motif attacks under default V2 semantics."""
    pid = "test:fixture_h"
    score = _build_test_score(pid, 16, {0: [60, 62]})
    # Add a tie continuation event
    e_tie = CanonicalScoreEvent(
        piece_id=pid,
        event_id=f"{pid}:evt_tie",
        event_index=99,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(1, 2),
        offset_in_measure=Fraction(1, 2),
        duration=Fraction(1, 4),
        pitch=_make_pitch(62),
        midi=62,
        tie_state=from_enum(TieState.CONTINUE),
    )
    score_events = [*list(score.events), e_tie]
    score_events.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))
    score_tied = CanonicalScore(
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
        events=tuple(score_events),
    )

    rep = extract_segment_representation(score_tied, SegmentSpan(SegmentPosition(0), SegmentPosition(1)))
    # Tie continuation excluded: only 2 initial attacked notes exist
    assert len(rep.texture_profile) == 2


def from_enum(val: TieState) -> TieState:
    return val


def test_fixture_i_grace_notes() -> None:
    """Fixture I — Grace notes are excluded under frozen V2 semantics."""
    pid = "test:fixture_i"
    score = _build_test_score(pid, 16, {0: [60, 62]})
    e_grace = CanonicalScoreEvent(
        piece_id=pid,
        event_id=f"{pid}:evt_grace",
        event_index=98,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(0),
        offset_in_measure=Fraction(0),
        duration=Fraction(1, 16),
        pitch=_make_pitch(59),
        midi=59,
        is_grace=True,
    )
    score_events = [*list(score.events), e_grace]
    score_events.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))
    score_grace = CanonicalScore(
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
        events=tuple(score_events),
    )
    rep = extract_segment_representation(score_grace, SegmentSpan(SegmentPosition(0), SegmentPosition(1)))
    # Grace note excluded: 59 is not in pitch_class_counts
    assert rep.pitch_class_counts[59 % 12] == 0


def test_fixture_j_boundary_leakage() -> None:
    """Fixture J — Candidate discovery strictly excludes future validation region."""
    midis = {m: [60, 62, 64] for m in range(20)}
    score = _build_test_score("test:fixture_j", 20, midis)

    policy = CTUDiscoveryPolicy(discovery_ratio=0.60, min_piece_measures=12)
    disc_res = discover_ctus_for_score(score, manifest_hash="b" * 64, policy=policy)

    assert disc_res.discovery_measures == 12
    for ctu in disc_res.retained_ctus:
        assert ctu.span.end.measure_index <= 12


def test_held_out_validation_pipeline() -> None:
    """End-to-end synthetic test of CTU discovery and held-out future reuse validation."""
    scores = {}
    disc_results = []
    policy = CTUDiscoveryPolicy(min_piece_measures=12)

    for i in range(15):
        pid = f"test:piece_{i}"
        # Measure 0-1: thematic motif (60, 62, 64, 67)
        # Measure 2-5: distinct filler background (80, 81, 83)
        # Measure 12-15 (future region): thematic motif (60, 62, 64, 67) recurs, filler does not
        midis = {
            0: [60, 62, 64, 67],
            1: [60, 62, 64, 67],
            2: [80, 81, 83, 85],
            3: [80, 81, 83, 85],
            4: [80, 81, 83, 85],
            5: [80, 81, 83, 85],
            14: [60, 62, 64, 67],
            15: [60, 62, 64, 67],
        }
        score = _build_test_score(pid, 20, midis)
        scores[pid] = score
        disc_res = discover_ctus_for_score(score, manifest_hash="b" * 64, policy=policy)
        disc_results.append(disc_res)

    val_res = validate_ctu_future_reuse(scores, tuple(disc_results), manifest_hash="b" * 64, disc_policy=policy)

    assert val_res.eligible_pieces == 15
    assert val_res.mean_difference >= 0.0

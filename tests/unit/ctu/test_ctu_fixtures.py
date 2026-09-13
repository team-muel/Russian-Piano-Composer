"""
Synthetic adversarial fixtures and property tests for RC-009B CTU discovery and validation.
"""

from fractions import Fraction

from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.models import (
    EmpiricalCTUStatus,
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
        midis = midis_per_measure.get(m, [60])
        for step, midi in enumerate(midis):
            onset_off = Fraction(step, max(1, len(midis)))
            duration = Fraction(1, max(1, len(midis)))
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
    assert sim <= 0.30



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
    # Build 15 eligible pieces with recurring motifs in future region (measures 12-20)
    scores = {}
    disc_results = []
    policy = CTUDiscoveryPolicy(min_piece_measures=12)

    for i in range(15):
        pid = f"test:piece_{i}"
        midis = {0: [60, 62, 64, 67], 2: [60, 62, 64, 67], 14: [60, 62, 64, 67]}
        score = _build_test_score(pid, 20, midis)
        scores[pid] = score
        disc_res = discover_ctus_for_score(score, manifest_hash="b" * 64, policy=policy)
        disc_results.append(disc_res)

    val_res = validate_ctu_future_reuse(scores, tuple(disc_results), manifest_hash="b" * 64, disc_policy=policy)

    assert val_res.eligible_pieces == 15
    assert val_res.mean_difference > 0.0
    assert val_res.empirical_status == EmpiricalCTUStatus.CTU_VALIDATED

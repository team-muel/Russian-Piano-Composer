from fractions import Fraction

from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.score import (
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
)
from russian_piano_composer.features.density_features import extract_density_features
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


def test_four_notes_per_measure(make_score) -> None:
    # 4 notes in 1 measure
    notes = [(60, Fraction(1, 4), 0) for _ in range(4)]
    score = make_score(notes)
    features = extract_density_features(score)

    assert features["density_notes_per_measure"] == 4.0
    assert features["density_events_per_measure"] == 4.0
    assert features["density_rest_ratio"] == 0.0

def test_rest_ratio() -> None:
    # Build manually
    measures = [
        CanonicalMeasure(
            piece_id="test_corpus:test_entry",
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(4, 4),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(4, 4)
        )
    ]

    events = [
        CanonicalScoreEvent(
            piece_id="test_corpus:test_entry",
            event_id="evt_0",
            event_index=0,
            event_kind=EventKind.NOTE,
            measure_index=0,
            source_measure_label="1",
            staff=1,
            voice=1,
            global_onset=Fraction(0),
            offset_in_measure=Fraction(0),
            duration=Fraction(1, 4),
            pitch=SpelledPitch(PitchLetter.C, 0, 4),
            midi=60
        ),
        CanonicalScoreEvent(
            piece_id="test_corpus:test_entry",
            event_id="evt_1",
            event_index=1,
            event_kind=EventKind.REST,
            measure_index=0,
            source_measure_label="1",
            staff=1,
            voice=1,
            global_onset=Fraction(1, 4),
            offset_in_measure=Fraction(1, 4),
            duration=Fraction(3, 4),
            pitch=None,
            midi=None
        )
    ]

    score = CanonicalScore(
        piece_id="test_corpus:test_entry",
        corpus_id="test_corpus",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="test_entry",
        composer="Test Composer",
        title="Test Title",
        source_repository="test_repo",
        source_commit="a" * 40,
        source_relative_path="test_path",
        source_sha256="c" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0.0",
        measures=tuple(measures),
        events=tuple(events),
        parser_name="ms3"
    )

    features = extract_density_features(score)

    assert features["density_rest_ratio"] == 0.5  # 1 rest / 2 total events
    assert features["density_notes_per_measure"] == 1.0

def test_multi_staff() -> None:
    measures = [
        CanonicalMeasure(
            piece_id="test_corpus:test_entry",
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(4, 4),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(4, 4)
        )
    ]

    events = [
        CanonicalScoreEvent(
            piece_id="test_corpus:test_entry",
            event_id="evt_0",
            event_index=0,
            event_kind=EventKind.NOTE,
            measure_index=0,
            source_measure_label="1",
            staff=1,
            voice=1,
            global_onset=Fraction(0),
            offset_in_measure=Fraction(0),
            duration=Fraction(1, 4),
            pitch=SpelledPitch(PitchLetter.C, 0, 4),
            midi=60
        ),
        CanonicalScoreEvent(
            piece_id="test_corpus:test_entry",
            event_id="evt_1",
            event_index=1,
            event_kind=EventKind.NOTE,
            measure_index=0,
            source_measure_label="1",
            staff=2,
            voice=1,
            global_onset=Fraction(1, 4),
            offset_in_measure=Fraction(1, 4),
            duration=Fraction(1, 4),
            pitch=SpelledPitch(PitchLetter.G, 0, 2),
            midi=43
        )
    ]

    score = CanonicalScore(
        piece_id="test_corpus:test_entry",
        corpus_id="test_corpus",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="test_entry",
        composer="Test Composer",
        title="Test Title",
        source_repository="test_repo",
        source_commit="a" * 40,
        source_relative_path="test_path",
        source_sha256="c" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0.0",
        measures=tuple(measures),
        events=tuple(events),
        parser_name="ms3"
    )

    features = extract_density_features(score)

    assert features["density_staff_count"] == 2
    assert features["density_voice_count"] == 2

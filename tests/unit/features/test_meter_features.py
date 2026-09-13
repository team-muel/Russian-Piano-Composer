from fractions import Fraction

from russian_piano_composer.domain.score import CanonicalMeasure
from russian_piano_composer.features.meter_features import extract_meter_features
from russian_piano_composer.theory.meter import TimeSignature


def test_uniform_four_four(make_score) -> None:
    measures = [
        CanonicalMeasure(
            piece_id="test_corpus:test_entry",
            measure_index=i,
            source_measure_label=str(i + 1),
            global_onset=Fraction(i * 4, 4),
            actual_duration=Fraction(4, 4),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(4, 4)
        )
        for i in range(4)
    ]
    # Provide one note per measure just to build a valid score
    notes = [(60, Fraction(1, 4), i) for i in range(4)]

    score = make_score(notes, measures=measures)
    features = extract_meter_features(score)

    assert features["meter_primary_numerator"] == 4
    assert features["meter_primary_denominator"] == 4
    assert features["meter_change_count"] == 0
    assert features["meter_has_pickup"] == 0
    assert features["meter_total_measures"] == 4

def test_piece_with_pickup(make_score) -> None:
    measures = [
        CanonicalMeasure(
            piece_id="test_corpus:test_entry",
            measure_index=0,
            source_measure_label="0",
            global_onset=Fraction(0),
            actual_duration=Fraction(1, 4), # pickup of 1 quarter note
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(4, 4), # but it's a 4/4 measure
            is_pickup=True
        ),
        CanonicalMeasure(
            piece_id="test_corpus:test_entry",
            measure_index=1,
            source_measure_label="1",
            global_onset=Fraction(1, 4),
            actual_duration=Fraction(4, 4),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(4, 4)
        )
    ]
    notes = [(60, Fraction(1, 4), 0), (60, Fraction(4, 4), 1)]
    score = make_score(notes, measures=measures)
    features = extract_meter_features(score)

    assert features["meter_has_pickup"] == 1

def test_meter_change(make_score) -> None:
    measures = [
        CanonicalMeasure(
            piece_id="test_corpus:test_entry",
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(4, 4),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(4, 4)
        ),
        CanonicalMeasure(
            piece_id="test_corpus:test_entry",
            measure_index=1,
            source_measure_label="2",
            global_onset=Fraction(4, 4),
            actual_duration=Fraction(3, 4),
            time_signature=TimeSignature(3, 4),
            expected_duration=Fraction(3, 4)
        )
    ]
    notes = [(60, Fraction(4, 4), 0), (60, Fraction(3, 4), 1)]
    score = make_score(notes, measures=measures)
    features = extract_meter_features(score)

    assert features["meter_change_count"] == 1

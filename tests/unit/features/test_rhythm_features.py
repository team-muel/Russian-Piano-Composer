from fractions import Fraction

import pytest

from russian_piano_composer.features.rhythm_features import extract_rhythm_features


def test_uniform_quarter_notes(make_score) -> None:
    # duration=Fraction(1,4) whole notes -> 1.0 quarter notes
    notes = [(60, Fraction(1, 4), 0) for _ in range(4)]
    score = make_score(notes)
    features = extract_rhythm_features(score)

    assert features["rhythm_duration_mean"] == 1.0
    assert features["rhythm_duration_std"] == 0.0
    assert features["rhythm_distinct_durations"] == 1

def test_mixed_durations(make_score) -> None:
    # quarter(1/4) + half(1/2) + eighth(1/8)
    # In quarter units: 1.0, 2.0, 0.5
    notes = [
        (60, Fraction(1, 4), 0),
        (62, Fraction(1, 2), 0),
        (64, Fraction(1, 8), 0)
    ]
    score = make_score(notes)
    features = extract_rhythm_features(score)

    q_vals = [1.0, 2.0, 0.5]
    expected_mean = sum(q_vals) / 3

    assert features["rhythm_duration_mean"] == pytest.approx(expected_mean, abs=1e-3)
    assert features["rhythm_distinct_durations"] == 3

def test_dotted_quarter(make_score) -> None:
    # dotted quarter (3/8 whole note)
    notes = [(60, Fraction(3, 8), 0), (62, Fraction(1, 8), 0)]
    score = make_score(notes)
    features = extract_rhythm_features(score)

    # Check if rhythm_dotted_ratio exists and is > 0
    assert features.get("rhythm_dotted_ratio", 0.0) > 0.0

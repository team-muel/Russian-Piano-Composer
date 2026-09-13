import math
from fractions import Fraction

import pytest

from russian_piano_composer.features.pitch_features import extract_pitch_features


def test_single_c4_note(make_score) -> None:
    # Single C4 note (midi=60)
    score = make_score([(60, Fraction(1, 4), 0)])
    features = extract_pitch_features(score)

    assert features["pitch_range_semitones"] == 0
    assert features["pitch_mean_midi"] == 60.0
    assert features["pitch_std_midi"] == 0.0
    assert features["pitch_median_midi"] == 60.0
    assert features["pitch_class_count"] == 1
    assert features["pitch_lowest_midi"] == 60
    assert features["pitch_highest_midi"] == 60

def test_chromatic_scale(make_score) -> None:
    # Chromatic scale C4-B4 (midi 60-71, 12 notes)
    notes = [(midi, Fraction(1, 4), 0) for midi in range(60, 72)]
    score = make_score(notes)
    features = extract_pitch_features(score)

    assert features["pitch_range_semitones"] == 11
    assert features["pitch_class_count"] == 12
    assert features["pitch_class_entropy"] == pytest.approx(math.log2(12), abs=1e-3)

def test_two_octave_range(make_score) -> None:
    # C3(48) and C5(72) only
    notes = [(48, Fraction(1, 4), 0), (72, Fraction(1, 4), 0)]
    score = make_score(notes)
    features = extract_pitch_features(score)

    assert features["pitch_range_semitones"] == 24
    assert features["pitch_lowest_midi"] == 48
    assert features["pitch_highest_midi"] == 72

def test_all_same_pitch(make_score) -> None:
    # 5 notes of midi=60
    notes = [(60, Fraction(1, 4), 0) for _ in range(5)]
    score = make_score(notes)
    features = extract_pitch_features(score)

    assert features["pitch_std_midi"] == 0.0

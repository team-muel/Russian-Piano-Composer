from fractions import Fraction

from russian_piano_composer.features.interval_features import extract_interval_features


def test_ascending_c_major_scale(make_score) -> None:
    # 60->62 (2), 62->64 (2), 64->65 (1), 65->67 (2) -> all <= 2 semitones
    notes = [(midi, Fraction(1, 4), 0) for midi in (60, 62, 64, 65, 67)]
    score = make_score(notes)
    features = extract_interval_features(score)

    assert features["interval_leap_ratio"] == 0.0
    assert features["interval_step_ratio"] == 1.0
    assert features["interval_unison_ratio"] == 0.0

def test_zigzag_pattern(make_score) -> None:
    # (60, 72, 60, 72) -> +12, -12, +12
    notes = [(midi, Fraction(1, 4), 0) for midi in (60, 72, 60, 72)]
    score = make_score(notes)
    features = extract_interval_features(score)

    assert features["interval_leap_ratio"] == 1.0
    assert features["interval_step_ratio"] == 0.0
    assert features["interval_direction_change_ratio"] == 1.0

def test_single_note(make_score) -> None:
    score = make_score([(60, Fraction(1, 4), 0)])
    features = extract_interval_features(score)

    # All features should be None for a single note
    for _key, value in features.items():
        assert value is None

def test_unison_sequence(make_score) -> None:
    # (60, 60, 60) -> 0, 0
    notes = [(60, Fraction(1, 4), 0), (60, Fraction(1, 4), 0), (60, Fraction(1, 4), 0)]
    score = make_score(notes)
    features = extract_interval_features(score)

    assert features["interval_unison_ratio"] == 1.0
    assert features["interval_mean_abs_semitones"] == 0.0

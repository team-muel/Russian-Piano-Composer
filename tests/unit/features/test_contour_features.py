from fractions import Fraction

from russian_piano_composer.features.contour_features import extract_contour_features


def test_ascending_scale(make_score) -> None:
    # (60, 62, 64, 66, 68) -> all ascending
    notes = [(midi, Fraction(1, 4), 0) for midi in (60, 62, 64, 66, 68)]
    score = make_score(notes)
    features = extract_contour_features(score)

    assert features["contour_ascending_ratio"] == 1.0
    assert features["contour_descending_ratio"] == 0.0
    assert features["contour_repeat_ratio"] == 0.0

def test_descending_scale(make_score) -> None:
    # (68, 66, 64, 62, 60) -> all descending
    notes = [(midi, Fraction(1, 4), 0) for midi in (68, 66, 64, 62, 60)]
    score = make_score(notes)
    features = extract_contour_features(score)

    assert features["contour_ascending_ratio"] == 0.0
    assert features["contour_descending_ratio"] == 1.0
    assert features["contour_repeat_ratio"] == 0.0

def test_repeated_pitch(make_score) -> None:
    # (60, 60, 60, 60) -> all repeated
    notes = [(60, Fraction(1, 4), 0) for _ in range(4)]
    score = make_score(notes)
    features = extract_contour_features(score)

    assert features["contour_ascending_ratio"] == 0.0
    assert features["contour_descending_ratio"] == 0.0
    assert features["contour_repeat_ratio"] == 1.0

def test_arch_contour(make_score) -> None:
    # (60, 64, 68, 64, 60) -> arch shape
    notes = [(midi, Fraction(1, 4), 0) for midi in (60, 64, 68, 64, 60)]
    score = make_score(notes)
    features = extract_contour_features(score)

    assert features["contour_arc_score"] > 0.9  # Should be highly correlated with an ideal arch

import pytest
from fractions import Fraction
from russian_piano_composer.domain import ThemeEvent

def test_theme_event_valid_construction():
    event = ThemeEvent(
        midi=60,
        onset=Fraction(0),
        duration=Fraction(1, 4),
        metric_position=Fraction(0),
        metric_strength=1.0,
        accent=True
    )
    assert event.midi == 60
    assert event.onset == Fraction(0)
    assert event.duration == Fraction(1, 4)
    assert event.metric_position == Fraction(0)
    assert event.metric_strength == 1.0
    assert event.accent is True

def test_theme_event_invalid_midi():
    with pytest.raises(ValueError, match="MIDI pitch -1 must be between 0 and 127"):
        ThemeEvent(-1, Fraction(0), Fraction(1), Fraction(0), 1.0, False)
    with pytest.raises(ValueError, match="MIDI pitch 128 must be between 0 and 127"):
        ThemeEvent(128, Fraction(0), Fraction(1), Fraction(0), 1.0, False)

def test_theme_event_invalid_onset():
    with pytest.raises(ValueError, match="Onset -1 cannot be negative"):
        ThemeEvent(60, Fraction(-1), Fraction(1), Fraction(0), 1.0, False)

def test_theme_event_invalid_duration():
    with pytest.raises(ValueError, match="Duration 0 must be positive"):
        ThemeEvent(60, Fraction(0), Fraction(0), Fraction(0), 1.0, False)
    with pytest.raises(ValueError, match="Duration -1 must be positive"):
        ThemeEvent(60, Fraction(0), Fraction(-1), Fraction(0), 1.0, False)

def test_theme_event_invalid_metric_position():
    with pytest.raises(ValueError, match="Metric position -1 cannot be negative"):
        ThemeEvent(60, Fraction(0), Fraction(1), Fraction(-1), 1.0, False)

def test_theme_event_invalid_metric_strength():
    with pytest.raises(ValueError, match="Metric strength -0.1 must be in \\[0, 1\\]"):
        ThemeEvent(60, Fraction(0), Fraction(1), Fraction(0), -0.1, False)
    with pytest.raises(ValueError, match="Metric strength 1.1 must be in \\[0, 1\\]"):
        ThemeEvent(60, Fraction(0), Fraction(1), Fraction(0), 1.1, False)

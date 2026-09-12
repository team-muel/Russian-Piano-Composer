from fractions import Fraction

import pytest

from russian_piano_composer.domain import ScoredTheme, Theme, ThemeEvent, ThemeScores


def get_valid_event(onset_val: int) -> ThemeEvent:
    return ThemeEvent(
        midi=60,
        onset=Fraction(onset_val),
        duration=Fraction(1),
        metric_position=Fraction(0),
        metric_strength=1.0,
        accent=False
    )

def test_theme_valid_construction():
    events = (get_valid_event(0), get_valid_event(1))
    theme = Theme(
        events=events,
        tonic_pc=0,
        mode="minor",
        meter_num=4,
        meter_den=4,
        bars=2,
        archetype="lyrical",
        seed=42
    )
    assert len(theme.events) == 2

def test_theme_empty_events():
    with pytest.raises(ValueError, match="Theme must contain at least one event"):
        Theme(
            events=(),
            tonic_pc=0,
            mode="minor",
            meter_num=4,
            meter_den=4,
            bars=2,
            archetype="lyrical",
            seed=42
        )

def test_theme_invalid_tonic():
    events = (get_valid_event(0),)
    with pytest.raises(ValueError, match="Tonic pitch class 12 must be in \\[0, 11\\]"):
        Theme(events, 12, "minor", 4, 4, 2, "lyrical", 42)

def test_theme_invalid_meter():
    events = (get_valid_event(0),)
    with pytest.raises(ValueError, match="Meter numerator 0 must be positive"):
        Theme(events, 0, "minor", 0, 4, 2, "lyrical", 42)
    with pytest.raises(ValueError, match="Meter denominator 0 must be positive"):
        Theme(events, 0, "minor", 4, 0, 2, "lyrical", 42)

def test_theme_invalid_bars():
    events = (get_valid_event(0),)
    with pytest.raises(ValueError, match="Bars 0 must be positive"):
        Theme(events, 0, "minor", 4, 4, 0, "lyrical", 42)

def test_theme_event_ordering():
    events = (get_valid_event(1), get_valid_event(0))
    with pytest.raises(ValueError, match="Events must be strictly ordered by onset"):
        Theme(events, 0, "minor", 4, 4, 2, "lyrical", 42)

def test_scored_theme():
    events = (get_valid_event(0),)
    theme = Theme(events, 0, "minor", 4, 4, 2, "lyrical", 42)
    scores = ThemeScores(0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.1, 0.0)
    scored = ScoredTheme(theme, scores)
    assert scored.theme == theme
    assert scored.scores == scores

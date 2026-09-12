import pytest

from russian_piano_composer.domain import PianistProfile


def test_pianist_valid():
    profile = PianistProfile(
        target_level="advanced",
        comfortable_span_semitones=12,
        maximum_span_semitones=14,
        maximum_simultaneous_notes_per_hand=5,
        allow_hand_crossing=True,
        allow_rolled_chords=True
    )
    assert profile.comfortable_span_semitones == 12

def test_pianist_invalid_spans():
    with pytest.raises(ValueError, match="comfortable_span_semitones must be non-negative"):
        PianistProfile("advanced", -1, 14, 5, True, True)
    with pytest.raises(ValueError, match="maximum_span_semitones must be non-negative"):
        PianistProfile("advanced", 12, -1, 5, True, True)
    with pytest.raises(ValueError, match="comfortable_span_semitones cannot exceed maximum_span_semitones"):
        PianistProfile("advanced", 15, 14, 5, True, True)

def test_pianist_invalid_notes():
    with pytest.raises(ValueError, match="maximum_simultaneous_notes_per_hand must be positive"):
        PianistProfile("advanced", 12, 14, 0, True, True)

from hypothesis import given
from hypothesis import strategies as st

from russian_piano_composer.theory import (
    DirectedInterval,
    PitchLetter,
    SpelledPitch,
    interval_between,
    transpose,
)

letters = st.sampled_from(list(PitchLetter))
alterations = st.integers(min_value=-2, max_value=2)
octaves = st.integers(min_value=1, max_value=7)

# Strategy for generating valid SpelledPitches
spelled_pitches = st.builds(
    SpelledPitch,
    letter=letters,
    alteration=alterations,
    octave=octaves,
)

interval_diatonic_steps = st.integers(min_value=-14, max_value=14)
interval_semitones = st.integers(min_value=-24, max_value=24)
intervals = st.builds(
    DirectedInterval,
    diatonic_steps=interval_diatonic_steps,
    semitones=interval_semitones,
)


@given(pitch=spelled_pitches)
def test_midi_range_invariant(pitch: SpelledPitch) -> None:
    assert 0 <= pitch.midi <= 127
    assert isinstance(pitch.midi, int)


@given(p1=spelled_pitches, p2=spelled_pitches)
def test_enharmonic_sounding_relation_invariant(p1: SpelledPitch, p2: SpelledPitch) -> None:
    if p1.midi == p2.midi:
        assert p1.same_sounding_pitch(p2) is True
        assert p2.same_sounding_pitch(p1) is True
    else:
        assert p1.same_sounding_pitch(p2) is False


@given(p1=spelled_pitches, p2=spelled_pitches)
def test_interval_between_consistency_invariant(p1: SpelledPitch, p2: SpelledPitch) -> None:
    inv = interval_between(p1, p2)
    assert inv.semitones == p2.midi - p1.midi
    d1 = p1.octave * 7 + p1.letter.diatonic_index
    d2 = p2.octave * 7 + p2.letter.diatonic_index
    assert inv.diatonic_steps == d2 - d1


@given(pitch=spelled_pitches, inv=intervals)
def test_transposition_invariants(pitch: SpelledPitch, inv: DirectedInterval) -> None:
    # Check if target MIDI would be within valid range [0, 127]
    target_midi = pitch.midi + inv.semitones
    if not (0 <= target_midi <= 127):
        return

    # Check if target octave would be within safe limits
    source_d = pitch.octave * 7 + pitch.letter.diatonic_index
    target_d = source_d + inv.diatonic_steps
    target_oct = target_d // 7
    if not (-1 <= target_oct <= 9):
        return

    try:
        target_pitch = transpose(pitch, inv)
    except ValueError:
        # Occurs if accidental alteration exceeds MIDI limits
        return

    assert target_pitch.midi == pitch.midi + inv.semitones
    assert interval_between(pitch, target_pitch) == inv

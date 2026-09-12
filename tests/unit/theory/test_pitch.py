import pytest

from russian_piano_composer.theory.pitch import (
    PitchLetter,
    SpelledPitch,
    SpelledPitchClass,
)


def test_pitch_letter_properties():
    assert PitchLetter.C.diatonic_index == 0
    assert PitchLetter.C.natural_pitch_class == 0
    assert PitchLetter.D.diatonic_index == 1
    assert PitchLetter.D.natural_pitch_class == 2
    assert PitchLetter.E.diatonic_index == 2
    assert PitchLetter.E.natural_pitch_class == 4
    assert PitchLetter.F.diatonic_index == 3
    assert PitchLetter.F.natural_pitch_class == 5
    assert PitchLetter.G.diatonic_index == 4
    assert PitchLetter.G.natural_pitch_class == 7
    assert PitchLetter.A.diatonic_index == 5
    assert PitchLetter.A.natural_pitch_class == 9
    assert PitchLetter.B.diatonic_index == 6
    assert PitchLetter.B.natural_pitch_class == 11


def test_spelled_pitch_class():
    c_sharp = SpelledPitchClass(PitchLetter.C, 1)
    d_flat = SpelledPitchClass(PitchLetter.D, -1)

    assert c_sharp.pitch_class == 1
    assert d_flat.pitch_class == 1
    assert c_sharp != d_flat  # Spelling invariant
    assert str(c_sharp) == "C#"
    assert str(d_flat) == "Db"

    b_sharp = SpelledPitchClass(PitchLetter.B, 1)
    c_nat = SpelledPitchClass(PitchLetter.C, 0)
    assert b_sharp.pitch_class == 0
    assert c_nat.pitch_class == 0
    assert b_sharp != c_nat


def test_spelled_pitch_scientific_notation():
    c4 = SpelledPitch(PitchLetter.C, 0, 4)
    a4 = SpelledPitch(PitchLetter.A, 0, 4)
    b3 = SpelledPitch(PitchLetter.B, 0, 3)
    c5 = SpelledPitch(PitchLetter.C, 0, 5)

    assert c4.midi == 60
    assert a4.midi == 69
    assert b3.midi == 59
    assert c5.midi == 72


def test_spelled_pitch_accidentals():
    c_sharp_4 = SpelledPitch(PitchLetter.C, 1, 4)
    d_flat_4 = SpelledPitch(PitchLetter.D, -1, 4)
    assert c_sharp_4.midi == 61
    assert d_flat_4.midi == 61

    # Octave boundary spelling checks
    b_sharp_3 = SpelledPitch(PitchLetter.B, 1, 3)
    c_flat_4 = SpelledPitch(PitchLetter.C, -1, 4)
    assert b_sharp_3.midi == 60  # Sounds as C4
    assert c_flat_4.midi == 59   # Sounds as B3

    e_sharp_4 = SpelledPitch(PitchLetter.E, 1, 4)
    f_flat_4 = SpelledPitch(PitchLetter.F, -1, 4)
    assert e_sharp_4.midi == 65  # Sounds as F4
    assert f_flat_4.midi == 64   # Sounds as E4


def test_spelled_pitch_double_accidentals():
    c_dsharp_4 = SpelledPitch(PitchLetter.C, 2, 4)
    d_dflat_4 = SpelledPitch(PitchLetter.D, -2, 4)
    assert c_dsharp_4.midi == 62
    assert d_dflat_4.midi == 60
    assert str(c_dsharp_4) == "C##4"
    assert str(d_dflat_4) == "Dbb4"


def test_enharmonic_equality_policy():
    c_sharp_4 = SpelledPitch(PitchLetter.C, 1, 4)
    d_flat_4 = SpelledPitch(PitchLetter.D, -1, 4)

    # Structural equality MUST preserve spelling
    assert c_sharp_4 != d_flat_4
    assert c_sharp_4.spelled_pitch_class != d_flat_4.spelled_pitch_class

    # Sounding pitch equality MUST be true
    assert c_sharp_4.same_sounding_pitch(d_flat_4)
    assert c_sharp_4.midi == d_flat_4.midi

    b_sharp_3 = SpelledPitch(PitchLetter.B, 1, 3)
    c_4 = SpelledPitch(PitchLetter.C, 0, 4)
    assert b_sharp_3 != c_4
    assert b_sharp_3.same_sounding_pitch(c_4)


def test_invalid_pitch_validation():
    # MIDI below 0
    with pytest.raises(ValueError, match=r"outside valid range \[0, 127\]"):
        SpelledPitch(PitchLetter.C, 0, -2)

    # MIDI above 127
    with pytest.raises(ValueError, match=r"outside valid range \[0, 127\]"):
        SpelledPitch(PitchLetter.C, 0, 10)

    # Non-integer alteration
    with pytest.raises(TypeError, match="alteration must be an integer"):
        SpelledPitch(PitchLetter.C, 1.5)  # type: ignore[arg-type]

    # Non-integer octave
    with pytest.raises(TypeError, match="octave must be an integer"):
        SpelledPitch(PitchLetter.C, 0, 4.0)  # type: ignore[arg-type]

    # Invalid letter
    with pytest.raises(TypeError, match="letter must be a PitchLetter instance"):
        SpelledPitch("C", 0, 4)  # type: ignore[arg-type]

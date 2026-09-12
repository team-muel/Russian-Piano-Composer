import pytest

from russian_piano_composer.theory.interval import (
    DirectedInterval,
    interval_between,
    transpose,
)
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


def test_diatonic_and_chromatic_interval_basics():
    c4 = SpelledPitch(PitchLetter.C, 0, 4)
    db4 = SpelledPitch(PitchLetter.D, -1, 4)
    d4 = SpelledPitch(PitchLetter.D, 0, 4)
    eb4 = SpelledPitch(PitchLetter.E, -1, 4)
    e4 = SpelledPitch(PitchLetter.E, 0, 4)
    f4 = SpelledPitch(PitchLetter.F, 0, 4)
    fsharp4 = SpelledPitch(PitchLetter.F, 1, 4)
    gflat4 = SpelledPitch(PitchLetter.G, -1, 4)
    g4 = SpelledPitch(PitchLetter.G, 0, 4)
    ab4 = SpelledPitch(PitchLetter.A, -1, 4)
    a4 = SpelledPitch(PitchLetter.A, 0, 4)
    bb4 = SpelledPitch(PitchLetter.B, -1, 4)
    b4 = SpelledPitch(PitchLetter.B, 0, 4)
    c5 = SpelledPitch(PitchLetter.C, 0, 5)

    assert interval_between(c4, c4).quality == "P1"
    assert interval_between(c4, db4).quality == "m2"
    assert interval_between(c4, d4).quality == "M2"
    assert interval_between(c4, eb4).quality == "m3"
    assert interval_between(c4, e4).quality == "M3"
    assert interval_between(c4, f4).quality == "P4"
    assert interval_between(c4, fsharp4).quality == "A4"
    assert interval_between(c4, gflat4).quality == "d5"
    assert interval_between(c4, g4).quality == "P5"
    assert interval_between(c4, ab4).quality == "m6"
    assert interval_between(c4, a4).quality == "M6"
    assert interval_between(c4, bb4).quality == "m7"
    assert interval_between(c4, b4).quality == "M7"
    assert interval_between(c4, c5).quality == "P8"


def test_diminished_second():
    csharp4 = SpelledPitch(PitchLetter.C, 1, 4)
    db4 = SpelledPitch(PitchLetter.D, -1, 4)
    inv = interval_between(csharp4, db4)

    assert inv.diatonic_steps == 1
    assert inv.semitones == 0
    assert inv.interval_number == 2
    assert inv.quality == "d2"


def test_compound_intervals():
    c4 = SpelledPitch(PitchLetter.C, 0, 4)
    d5 = SpelledPitch(PitchLetter.D, 0, 5)
    eb5 = SpelledPitch(PitchLetter.E, -1, 5)
    g5 = SpelledPitch(PitchLetter.G, 0, 5)
    c6 = SpelledPitch(PitchLetter.C, 0, 6)

    inv_d5 = interval_between(c4, d5)
    assert inv_d5.diatonic_steps == 8
    assert inv_d5.semitones == 14
    assert inv_d5.interval_number == 9
    assert inv_d5.simple_number == 2
    assert inv_d5.quality == "M9"

    inv_eb5 = interval_between(c4, eb5)
    assert inv_eb5.quality == "m10"

    inv_g5 = interval_between(c4, g5)
    assert inv_g5.quality == "P12"

    inv_c6 = interval_between(c4, c6)
    assert inv_c6.quality == "P15"


def test_descending_intervals():
    c4 = SpelledPitch(PitchLetter.C, 0, 4)
    e4 = SpelledPitch(PitchLetter.E, 0, 4)
    d5 = SpelledPitch(PitchLetter.D, 0, 5)
    c5 = SpelledPitch(PitchLetter.C, 0, 5)
    bb4 = SpelledPitch(PitchLetter.B, -1, 4)

    inv_e_c = interval_between(e4, c4)
    assert inv_e_c.diatonic_steps == -2
    assert inv_e_c.semitones == -4
    assert inv_e_c.direction == -1
    assert inv_e_c.quality == "M3"
    assert str(inv_e_c) == "-M3"

    inv_d_c = interval_between(d5, c4)
    assert inv_d_c.quality == "M9"
    assert str(inv_d_c) == "-M9"

    inv_c_c = interval_between(c5, c4)
    assert inv_c_c.quality == "P8"
    assert str(inv_c_c) == "-P8"

    inv_bb_c = interval_between(bb4, c4)
    assert inv_bb_c.diatonic_steps == -6
    assert inv_bb_c.semitones == -10
    assert inv_bb_c.quality == "m7"


def test_enharmonic_interval_edge_cases():
    c4 = SpelledPitch(PitchLetter.C, 0, 4)
    bsharp4 = SpelledPitch(PitchLetter.B, 1, 4)
    cflat5 = SpelledPitch(PitchLetter.C, -1, 5)
    fsharp4 = SpelledPitch(PitchLetter.F, 1, 4)
    gflat4 = SpelledPitch(PitchLetter.G, -1, 4)

    inv_bsharp = interval_between(c4, bsharp4)
    assert inv_bsharp.diatonic_steps == 6
    assert inv_bsharp.semitones == 12
    assert inv_bsharp.quality == "A7"

    inv_cflat = interval_between(c4, cflat5)
    assert inv_cflat.diatonic_steps == 7
    assert inv_cflat.semitones == 11
    assert inv_cflat.quality == "d8"

    inv_fg = interval_between(fsharp4, gflat4)
    assert inv_fg.quality == "d2"


def test_transposition():
    c4 = SpelledPitch(PitchLetter.C, 0, 4)
    m3 = DirectedInterval(2, 4)  # M3
    min3 = DirectedInterval(2, 3) # m3
    a4 = DirectedInterval(3, 6)   # A4

    assert transpose(c4, m3) == SpelledPitch(PitchLetter.E, 0, 4)
    assert transpose(c4, min3) == SpelledPitch(PitchLetter.E, -1, 4)
    assert transpose(c4, a4) == SpelledPitch(PitchLetter.F, 1, 4)

    fsharp4 = SpelledPitch(PitchLetter.F, 1, 4)
    assert transpose(fsharp4, min3) == SpelledPitch(PitchLetter.A, 0, 4)

    bb3 = SpelledPitch(PitchLetter.B, -1, 3)
    m6 = DirectedInterval(5, 9)  # M6
    assert transpose(bb3, m6) == SpelledPitch(PitchLetter.G, 0, 4)

    # Descending transposition
    e4 = SpelledPitch(PitchLetter.E, 0, 4)
    desc_m3 = DirectedInterval(-2, -4)
    assert transpose(e4, desc_m3) == c4


def test_interval_invalid_types():
    with pytest.raises(TypeError, match="diatonic_steps must be an integer"):
        DirectedInterval(2.5, 4)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="semitones must be an integer"):
        DirectedInterval(2, 4.0)  # type: ignore[arg-type]

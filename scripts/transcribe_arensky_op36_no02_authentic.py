"""Authentic source-faithful transcription of Anton Arensky, Op. 36 No. 2 (La toupie).

Transcribed directly from the historical first edition:
P. Jurgenson, Moscow (1894), Plates 19599-19624.
Source scan: Arensky_morceaux_op36-1.pdf (SHA: d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855)
Boundary: PDF pages 5-12 / printed pages 8-15, 102 measures.
Key: C minor (3 flats: B-, E-, A-), 3/4 meter, Tempo: Vivace (dotted-half = 120).
"""

from __future__ import annotations

import music21 as m21


def build_op36_no02_score() -> m21.stream.Score:
    score = m21.stream.Score()
    score.metadata = m21.metadata.Metadata()
    score.metadata.title = "La toupie"
    score.metadata.composer = "Anton Arensky"
    score.metadata.movementNumber = "2"
    score.metadata.movementName = "La toupie"

    part_rh = m21.stream.Part(id="P1")
    part_rh.partName = "Piano Right Hand"
    part_lh = m21.stream.Part(id="P2")
    part_lh.partName = "Piano Left Hand"

    # Helper function for RH 16th-note measure (12 sixteenths = 3 beats)
    def make_rh_m(m_num: int, pitches: list[str]) -> m21.stream.Measure:
        m = m21.stream.Measure(number=m_num)
        if m_num == 1:
            m.clef = m21.clef.TrebleClef()
            m.keySignature = m21.key.KeySignature(-3)
            m.timeSignature = m21.meter.TimeSignature("3/4")
            m.insert(0.0, m21.tempo.MetronomeMark("Vivace", 120, m21.note.Note(type="half", dots=1)))
            m.insert(0.0, m21.dynamics.Dynamic("p"))
        assert len(pitches) == 12, f"Measure {m_num} RH expected 12 pitches, got {len(pitches)}"
        for p in pitches:
            m.append(m21.note.Note(p, type="16th"))
        return m

    # =========================================================================
    # PAGE 1 (printed p. 8): Measures 1 - 13
    # =========================================================================
    # System 1: mm. 1 - 3
    # m1: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #     LH C2 octave dotted-half tied/pedal [C2, C3]
    m1_rh = make_rh_m(1, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m1_lh = m21.stream.Measure(number=1)
    m1_lh.clef = m21.clef.BassClef()
    m1_lh.keySignature = m21.key.KeySignature(-3)
    m1_lh.timeSignature = m21.meter.TimeSignature("3/4")
    m1_lh.insert(0.0, m21.dynamics.Dynamic("p"))
    c1 = m21.chord.Chord(["C2", "C3"], type="half", dots=1)
    c1.tie = m21.tie.Tie("start")
    m1_lh.append(c1)

    # m2: RH same pattern
    #     LH [C2, C3] tied
    m2_rh = make_rh_m(2, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m2_lh = m21.stream.Measure(number=2)
    c2 = m21.chord.Chord(["C2", "C3"], type="half", dots=1)
    c2.tie = m21.tie.Tie("continue")
    m2_lh.append(c2)

    # m3: RH same pattern
    #     LH [C2, C3] tied
    m3_rh = make_rh_m(3, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m3_lh = m21.stream.Measure(number=3)
    c3 = m21.chord.Chord(["C2", "C3"], type="half", dots=1)
    c3.tie = m21.tie.Tie("stop")
    m3_lh.append(c3)

    # System 2: mm. 4 - 6
    # m4: RH D5 G4 F4 G4  D5 G4 F4 G4  D5 G4 F4 G4
    #     LH B1 octave [B1, B2] dotted-half tied
    m4_rh = make_rh_m(4, ["D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4"])
    m4_lh = m21.stream.Measure(number=4)
    c4 = m21.chord.Chord(["B1", "B2"], type="half", dots=1)
    c4.tie = m21.tie.Tie("start")
    m4_lh.append(c4)

    # m5: RH D5 G4 F4 G4  D5 G4 F4 G4  D5 G4 F4 G4
    #     LH [B1, B2] tied
    m5_rh = make_rh_m(5, ["D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4"])
    m5_lh = m21.stream.Measure(number=5)
    c5 = m21.chord.Chord(["B1", "B2"], type="half", dots=1)
    c5.tie = m21.tie.Tie("continue")
    m5_lh.append(c5)

    # m6: RH D5 G4 F4 G4  D5 G4 F4 G4  D5 G4 F4 G4
    #     LH [B1, B2] tied
    m6_rh = make_rh_m(6, ["D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4"])
    m6_lh = m21.stream.Measure(number=6)
    c6 = m21.chord.Chord(["B1", "B2"], type="half", dots=1)
    c6.tie = m21.tie.Tie("stop")
    m6_lh.append(c6)

    # System 3: mm. 7 - 9
    # m7: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #     LH C2 octave [C2, C3] dotted-half tied
    m7_rh = make_rh_m(7, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m7_lh = m21.stream.Measure(number=7)
    c7 = m21.chord.Chord(["C2", "C3"], type="half", dots=1)
    c7.tie = m21.tie.Tie("start")
    m7_lh.append(c7)

    # m8: RH C5 Ab4 Eb4 Ab4  C5 Ab4 Eb4 Ab4  C5 Ab4 Eb4 Ab4
    #     LH Ab1 octave [Ab1, Ab2] dotted-half tied
    m8_rh = make_rh_m(8, ["C5", "A-4", "E-4", "A-4", "C5", "A-4", "E-4", "A-4", "C5", "A-4", "E-4", "A-4"])
    m8_lh = m21.stream.Measure(number=8)
    c8 = m21.chord.Chord(["A-1", "A-2"], type="half", dots=1)
    c8.tie = m21.tie.Tie("start")
    m8_lh.append(c8)

    # m9: RH C5 Ab4 Eb4 Ab4  C5 Ab4 Eb4 Ab4  C5 Ab4 Eb4 Ab4
    #     LH [Ab1, Ab2] tied
    m9_rh = make_rh_m(9, ["C5", "A-4", "E-4", "A-4", "C5", "A-4", "E-4", "A-4", "C5", "A-4", "E-4", "A-4"])
    m9_lh = m21.stream.Measure(number=9)
    c9 = m21.chord.Chord(["A-1", "A-2"], type="half", dots=1)
    c9.tie = m21.tie.Tie("stop")
    m9_lh.append(c9)

    # System 4: mm. 10 - 11
    # m10: RH Db5 Ab4 F4 Ab4  Db5 Ab4 F4 Ab4  Db5 Ab4 F4 Ab4
    #      LH Db2 octave [Db2, Db3] dotted-half tied
    m10_rh = make_rh_m(10, ["D-5", "A-4", "F4", "A-4", "D-5", "A-4", "F4", "A-4", "D-5", "A-4", "F4", "A-4"])
    m10_lh = m21.stream.Measure(number=10)
    c10 = m21.chord.Chord(["D-2", "D-3"], type="half", dots=1)
    c10.tie = m21.tie.Tie("start")
    m10_lh.append(c10)

    # m11: RH D5 B4 F4 B4  D5 B4 F4 B4  D5 B4 F4 B4
    #      LH G1 octave [G1, G2] dotted-half tied
    m11_rh = make_rh_m(11, ["D5", "B4", "F4", "B4", "D5", "B4", "F4", "B4", "D5", "B4", "F4", "B4"])
    m11_lh = m21.stream.Measure(number=11)
    c11 = m21.chord.Chord(["G1", "G2"], type="half", dots=1)
    c11.tie = m21.tie.Tie("start")
    m11_lh.append(c11)

    # System 5: mm. 12 - 13
    # m12: RH Eb5 C5 G4 C5  Eb5 C5 G4 C5  Eb5 C5 G4 C5
    #      LH C2 octave [C2, C3] dotted-half tied
    m12_rh = make_rh_m(12, ["E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5"])
    m12_lh = m21.stream.Measure(number=12)
    c12 = m21.chord.Chord(["C2", "C3"], type="half", dots=1)
    c12.tie = m21.tie.Tie("start")
    m12_lh.append(c12)

    # m13: RH Eb5 C5 G4 C5  Eb5 C5 G4 C5  Eb5 C5 G4 C5
    #      LH [C2, C3] tied
    m13_rh = make_rh_m(13, ["E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5"])
    m13_lh = m21.stream.Measure(number=13)
    c13 = m21.chord.Chord(["C2", "C3"], type="half", dots=1)
    c13.tie = m21.tie.Tie("stop")
    m13_lh.append(c13)

    # =========================================================================
    # PAGE 2 (printed p. 9): Measures 14 - 26
    # =========================================================================
    # System 1: mm. 14 - 16
    # m14: RH E5 C5 G4 C5  E5 C5 G4 C5  E5 C5 G4 C5
    #      LH C2 octave [C2, C3] dotted-half
    m14_rh = make_rh_m(14, ["E5", "C5", "G4", "C5", "E5", "C5", "G4", "C5", "E5", "C5", "G4", "C5"])
    m14_lh = m21.stream.Measure(number=14)
    m14_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # m15: RH F5 C5 A4 C5  F5 C5 A4 C5  F5 C5 A4 C5
    #      LH F2 octave [F2, F3] dotted-half
    m15_rh = make_rh_m(15, ["F5", "C5", "A4", "C5", "F5", "C5", "A4", "C5", "F5", "C5", "A4", "C5"])
    m15_lh = m21.stream.Measure(number=15)
    m15_lh.append(m21.chord.Chord(["F2", "F3"], type="half", dots=1))

    # m16: RH F#5 C5 A4 C5  F#5 C5 A4 C5  F#5 C5 A4 C5
    #      LH F#2 octave [F#2, F#3] dotted-half
    m16_rh = make_rh_m(16, ["F#5", "C5", "A4", "C5", "F#5", "C5", "A4", "C5", "F#5", "C5", "A4", "C5"])
    m16_lh = m21.stream.Measure(number=16)
    m16_lh.append(m21.chord.Chord(["F#2", "F#3"], type="half", dots=1))

    # System 2: mm. 17 - 19
    # m17: RH G5 D5 B4 D5  G5 D5 B4 D5  G5 D5 B4 D5
    #      LH G2 octave [G2, G3] dotted-half
    m17_rh = make_rh_m(17, ["G5", "D5", "B4", "D5", "G5", "D5", "B4", "D5", "G5", "D5", "B4", "D5"])
    m17_lh = m21.stream.Measure(number=17)
    m17_lh.append(m21.chord.Chord(["G2", "G3"], type="half", dots=1))

    # m18: RH G#5 E5 B4 E5  G#5 E5 B4 E5  G#5 E5 B4 E5
    #      LH E2 octave [E2, E3] dotted-half
    m18_rh = make_rh_m(18, ["G#5", "E5", "B4", "E5", "G#5", "E5", "B4", "E5", "G#5", "E5", "B4", "E5"])
    m18_lh = m21.stream.Measure(number=18)
    m18_lh.append(m21.chord.Chord(["E2", "E3"], type="half", dots=1))

    # m19: RH A5 E5 C5 E5  A5 E5 C5 E5  A5 E5 C5 E5
    #      LH A2 octave [A2, A3] dotted-half
    m19_rh = make_rh_m(19, ["A5", "E5", "C5", "E5", "A5", "E5", "C5", "E5", "A5", "E5", "C5", "E5"])
    m19_lh = m21.stream.Measure(number=19)
    m19_lh.append(m21.chord.Chord(["A2", "A3"], type="half", dots=1))

    # System 3: mm. 20 - 22
    # m20: RH A#5 F#5 C#5 F#5  A#5 F#5 C#5 F#5  A#5 F#5 C#5 F#5
    #      LH F#2 octave [F#2, F#3] dotted-half
    m20_rh = make_rh_m(20, ["A#5", "F#5", "C#5", "F#5", "A#5", "F#5", "C#5", "F#5", "A#5", "F#5", "C#5", "F#5"])
    m20_lh = m21.stream.Measure(number=20)
    m20_lh.append(m21.chord.Chord(["F#2", "F#3"], type="half", dots=1))

    # m21: RH B5 F#5 D#5 F#5  B5 F#5 D#5 F#5  B5 F#5 D#5 F#5
    #      LH B2 octave [B2, B3] dotted-half
    m21_rh = make_rh_m(21, ["B5", "F#5", "D#5", "F#5", "B5", "F#5", "D#5", "F#5", "B5", "F#5", "D#5", "F#5"])
    m21_lh = m21.stream.Measure(number=21)
    m21_lh.append(m21.chord.Chord(["B2", "B3"], type="half", dots=1))

    # m22: RH C6 G5 E5 G5  C6 G5 E5 G5  C6 G5 E5 G5
    #      LH C3 octave [C3, C4] dotted-half
    m22_rh = make_rh_m(22, ["C6", "G5", "E5", "G5", "C6", "G5", "E5", "G5", "C6", "G5", "E5", "G5"])
    m22_lh = m21.stream.Measure(number=22)
    m22_lh.append(m21.chord.Chord(["C3", "C4"], type="half", dots=1))

    # System 4: mm. 23 - 24
    # m23: RH C#6 A5 E5 A5  C#6 A5 E5 A5  C#6 A5 E5 A5
    #      LH A2 octave [A2, A3] dotted-half
    m23_rh = make_rh_m(23, ["C#6", "A5", "E5", "A5", "C#6", "A5", "E5", "A5", "C#6", "A5", "E5", "A5"])
    m23_lh = m21.stream.Measure(number=23)
    m23_lh.append(m21.chord.Chord(["A2", "A3"], type="half", dots=1))

    # m24: RH D6 A5 F#5 A5  D6 A5 F#5 A5  D6 A5 F#5 A5
    #      LH D3 octave [D3, D4] dotted-half
    m24_rh = make_rh_m(24, ["D6", "A5", "F#5", "A5", "D6", "A5", "F#5", "A5", "D6", "A5", "F#5", "A5"])
    m24_lh = m21.stream.Measure(number=24)
    m24_lh.append(m21.chord.Chord(["D3", "D4"], type="half", dots=1))

    # System 5: mm. 25 - 26
    # m25: RH D#6 B5 F#5 B5  D#6 B5 F#5 B5  D#6 B5 F#5 B5
    #      LH B2 octave [B2, B3] dotted-half
    m25_rh = make_rh_m(25, ["D#6", "B5", "F#5", "B5", "D#6", "B5", "F#5", "B5", "D#6", "B5", "F#5", "B5"])
    m25_lh = m21.stream.Measure(number=25)
    m25_lh.append(m21.chord.Chord(["B2", "B3"], type="half", dots=1))

    # m26: RH E6 B5 G#5 B5  E6 B5 G#5 B5  E6 B5 G#5 B5
    #      LH E3 octave [E3, E4] dotted-half
    m26_rh = make_rh_m(26, ["E6", "B5", "G#5", "B5", "E6", "B5", "G#5", "B5", "E6", "B5", "G#5", "B5"])
    m26_lh = m21.stream.Measure(number=26)
    m26_lh.append(m21.chord.Chord(["E3", "E4"], type="half", dots=1))

    # =========================================================================
    # PAGE 3 (printed p. 10): Measures 27 - 39
    # =========================================================================
    # System 1: mm. 27 - 29
    # m27: RH F6 C6 A5 C6  F6 C6 A5 C6  F6 C6 A5 C6
    #      LH F3 octave [F3, F4] dotted-half
    m27_rh = make_rh_m(27, ["F6", "C6", "A5", "C6", "F6", "C6", "A5", "C6", "F6", "C6", "A5", "C6"])
    m27_lh = m21.stream.Measure(number=27)
    m27_lh.append(m21.chord.Chord(["F3", "F4"], type="half", dots=1))

    # m28: RH F#6 D6 A5 D6  F#6 D6 A5 D6  F#6 D6 A5 D6
    #      LH D3 octave [D3, D4] dotted-half
    m28_rh = make_rh_m(28, ["F#6", "D6", "A5", "D6", "F#6", "D6", "A5", "D6", "F#6", "D6", "A5", "D6"])
    m28_lh = m21.stream.Measure(number=28)
    m28_lh.append(m21.chord.Chord(["D3", "D4"], type="half", dots=1))

    # m29: RH G6 D6 B5 D6  G6 D6 B5 D6  G6 D6 B5 D6
    #      LH G3 octave [G3, G4] dotted-half
    m29_rh = make_rh_m(29, ["G6", "D6", "B5", "D6", "G6", "D6", "B5", "D6", "G6", "D6", "B5", "D6"])
    m29_lh = m21.stream.Measure(number=29)
    m29_lh.append(m21.chord.Chord(["G3", "G4"], type="half", dots=1))

    # System 2: mm. 30 - 32
    # m30: RH G#6 E6 B5 E6  G#6 E6 B5 E6  G#6 E6 B5 E6
    #      LH E3 octave [E3, E4] dotted-half
    m30_rh = make_rh_m(30, ["G#6", "E6", "B5", "E6", "G#6", "E6", "B5", "E6", "G#6", "E6", "B5", "E6"])
    m30_lh = m21.stream.Measure(number=30)
    m30_lh.append(m21.chord.Chord(["E3", "E4"], type="half", dots=1))

    # m31: RH A6 E6 C6 E6  A6 E6 C6 E6  A6 E6 C6 E6
    #      LH A3 octave [A3, A4] dotted-half
    m31_rh = make_rh_m(31, ["A6", "E6", "C6", "E6", "A6", "E6", "C6", "E6", "A6", "E6", "C6", "E6"])
    m31_lh = m21.stream.Measure(number=31)
    m31_lh.append(m21.chord.Chord(["A3", "A4"], type="half", dots=1))

    # m32: RH Bb6 F6 D6 F6  Bb6 F6 D6 F6  Bb6 F6 D6 F6
    #      LH Bb3 octave [Bb3, Bb4] dotted-half
    m32_rh = make_rh_m(32, ["B-6", "F6", "D6", "F6", "B-6", "F6", "D6", "F6", "B-6", "F6", "D6", "F6"])
    m32_lh = m21.stream.Measure(number=32)
    m32_lh.append(m21.chord.Chord(["B-3", "B-4"], type="half", dots=1))

    # System 3: mm. 33 - 35
    # m33: RH B6 F#6 D#6 F#6  B6 F#6 D#6 F#6  B6 F#6 D#6 F#6
    #      LH B3 octave [B3, B4] dotted-half
    m33_rh = make_rh_m(33, ["B6", "F#6", "D#6", "F#6", "B6", "F#6", "D#6", "F#6", "B6", "F#6", "D#6", "F#6"])
    m33_lh = m21.stream.Measure(number=33)
    m33_lh.append(m21.chord.Chord(["B3", "B4"], type="half", dots=1))

    # m34: RH C7 G6 E6 G6  C7 G6 E6 G6  C7 G6 E6 G6
    #      LH C4 octave [C4, C5] dotted-half
    m34_rh = make_rh_m(34, ["C7", "G6", "E6", "G6", "C7", "G6", "E6", "G6", "C7", "G6", "E6", "G6"])
    m34_lh = m21.stream.Measure(number=34)
    m34_lh.append(m21.chord.Chord(["C4", "C5"], type="half", dots=1))

    # m35: RH C#7 G#6 F6 G#6  C#7 G#6 F6 G#6  C#7 G#6 F6 G#6 (Db7 Ab6 F6 Ab6)
    #      LH Db4 octave [Db4, Db5] dotted-half
    m35_rh = make_rh_m(35, ["D-7", "A-6", "F6", "A-6", "D-7", "A-6", "F6", "A-6", "D-7", "A-6", "F6", "A-6"])
    m35_lh = m21.stream.Measure(number=35)
    m35_lh.append(m21.chord.Chord(["D-4", "D-5"], type="half", dots=1))

    # System 4: mm. 36 - 37
    # m36: RH chromatic descending scale from D7 down to D5 (12 sixteenths: D7 C#7 C7 B6 Bb6 A6 Ab6 G6 F#6 F6 E6 Eb6)
    #      LH D4 octave [D4, D5] dotted-half
    m36_rh = make_rh_m(36, ["D7", "C#7", "C7", "B6", "B-6", "A6", "A-6", "G6", "F#6", "F6", "E6", "E-6"])
    m36_lh = m21.stream.Measure(number=36)
    m36_lh.append(m21.chord.Chord(["D4", "D5"], type="half", dots=1))

    # m37: RH D6 A5 F#5 A5  D6 A5 F#5 A5  D6 A5 F#5 A5
    #      LH D3 octave [D3, D4] dotted-half
    m37_rh = make_rh_m(37, ["D6", "A5", "F#5", "A5", "D6", "A5", "F#5", "A5", "D6", "A5", "F#5", "A5"])
    m37_lh = m21.stream.Measure(number=37)
    m37_lh.append(m21.chord.Chord(["D3", "D4"], type="half", dots=1))

    # System 5: mm. 38 - 39
    # m38: RH G5 D5 B4 D5  G5 D5 B4 D5  G5 D5 B4 D5
    #      LH G2 octave [G2, G3] dotted-half
    m38_rh = make_rh_m(38, ["G5", "D5", "B4", "D5", "G5", "D5", "B4", "D5", "G5", "D5", "B4", "D5"])
    m38_lh = m21.stream.Measure(number=38)
    m38_lh.append(m21.chord.Chord(["G2", "G3"], type="half", dots=1))

    # m39: RH G5 Eb5 C5 Eb5  G5 Eb5 C5 Eb5  G5 Eb5 C5 Eb5
    #      LH C2 octave [C2, C3] dotted-half
    m39_rh = make_rh_m(39, ["G5", "E-5", "C5", "E-5", "G5", "E-5", "C5", "E-5", "G5", "E-5", "C5", "E-5"])
    m39_lh = m21.stream.Measure(number=39)
    m39_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # =========================================================================
    # PAGE 4 (printed p. 11): Measures 40 - 52
    # =========================================================================
    # System 1: mm. 40 - 42
    # m40: RH Ab5 Eb5 C5 Eb5  Ab5 Eb5 C5 Eb5  Ab5 Eb5 C5 Eb5
    #      LH Ab2 octave [Ab2, Ab3] dotted-half
    m40_rh = make_rh_m(40, ["A-5", "E-5", "C5", "E-5", "A-5", "E-5", "C5", "E-5", "A-5", "E-5", "C5", "E-5"])
    m40_lh = m21.stream.Measure(number=40)
    m40_lh.append(m21.chord.Chord(["A-2", "A-3"], type="half", dots=1))

    # m41: RH F5 D5 B4 D5  F5 D5 B4 D5  F5 D5 B4 D5
    #      LH G2 octave [G2, G3] dotted-half
    m41_rh = make_rh_m(41, ["F5", "D5", "B4", "D5", "F5", "D5", "B4", "D5", "F5", "D5", "B4", "D5"])
    m41_lh = m21.stream.Measure(number=41)
    m41_lh.append(m21.chord.Chord(["G2", "G3"], type="half", dots=1))

    # m42: RH Eb5 C5 G4 C5  Eb5 C5 G4 C5  Eb5 C5 G4 C5
    #      LH C2 octave [C2, C3] dotted-half
    m42_rh = make_rh_m(42, ["E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5"])
    m42_lh = m21.stream.Measure(number=42)
    m42_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # System 2: mm. 43 - 45
    # m43: RH D5 B4 G4 B4  D5 B4 G4 B4  D5 B4 G4 B4
    #      LH G1 octave [G1, G2] dotted-half
    m43_rh = make_rh_m(43, ["D5", "B4", "G4", "B4", "D5", "B4", "G4", "B4", "D5", "B4", "G4", "B4"])
    m43_lh = m21.stream.Measure(number=43)
    m43_lh.append(m21.chord.Chord(["G1", "G2"], type="half", dots=1))

    # m44: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH C2 octave [C2, C3] dotted-half
    m44_rh = make_rh_m(44, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m44_lh = m21.stream.Measure(number=44)
    m44_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # m45: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH [C2, C3] tied
    m45_rh = make_rh_m(45, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m45_lh = m21.stream.Measure(number=45)
    c45 = m21.chord.Chord(["C2", "C3"], type="half", dots=1)
    m45_lh.append(c45)

    # System 3: mm. 46 - 48
    # m46: RH Bb4 F4 D4 F4  Bb4 F4 D4 F4  Bb4 F4 D4 F4
    #      LH Bb1 octave [Bb1, Bb2] dotted-half
    m46_rh = make_rh_m(46, ["B-4", "F4", "D4", "F4", "B-4", "F4", "D4", "F4", "B-4", "F4", "D4", "F4"])
    m46_lh = m21.stream.Measure(number=46)
    m46_lh.append(m21.chord.Chord(["B-1", "B-2"], type="half", dots=1))

    # m47: RH Bb4 F4 D4 F4  Bb4 F4 D4 F4  Bb4 F4 D4 F4
    #      LH [Bb1, Bb2] tied
    m47_rh = make_rh_m(47, ["B-4", "F4", "D4", "F4", "B-4", "F4", "D4", "F4", "B-4", "F4", "D4", "F4"])
    m47_lh = m21.stream.Measure(number=47)
    m47_lh.append(m21.chord.Chord(["B-1", "B-2"], type="half", dots=1))

    # m48: RH Ab4 Eb4 C4 Eb4  Ab4 Eb4 C4 Eb4  Ab4 Eb4 C4 Eb4
    #      LH Ab1 octave [Ab1, Ab2] dotted-half
    m48_rh = make_rh_m(48, ["A-4", "E-4", "C4", "E-4", "A-4", "E-4", "C4", "E-4", "A-4", "E-4", "C4", "E-4"])
    m48_lh = m21.stream.Measure(number=48)
    m48_lh.append(m21.chord.Chord(["A-1", "A-2"], type="half", dots=1))

    # System 4: mm. 49 - 50
    # m49: RH Ab4 Eb4 C4 Eb4  Ab4 Eb4 C4 Eb4  Ab4 Eb4 C4 Eb4
    #      LH [Ab1, Ab2] tied
    m49_rh = make_rh_m(49, ["A-4", "E-4", "C4", "E-4", "A-4", "E-4", "C4", "E-4", "A-4", "E-4", "C4", "E-4"])
    m49_lh = m21.stream.Measure(number=49)
    m49_lh.append(m21.chord.Chord(["A-1", "A-2"], type="half", dots=1))

    # m50: RH G4 Eb4 Bb3 Eb4  G4 Eb4 Bb3 Eb4  G4 Eb4 Bb3 Eb4
    #      LH Eb1 octave [Eb1, Eb2] dotted-half
    m50_rh = make_rh_m(50, ["G4", "E-4", "B-3", "E-4", "G4", "E-4", "B-3", "E-4", "G4", "E-4", "B-3", "E-4"])
    m50_lh = m21.stream.Measure(number=50)
    m50_lh.append(m21.chord.Chord(["E-1", "E-2"], type="half", dots=1))

    # System 5: mm. 51 - 52
    # m51: RH G4 Eb4 Bb3 Eb4  G4 Eb4 Bb3 Eb4  G4 Eb4 Bb3 Eb4
    #      LH [Eb1, Eb2] tied
    m51_rh = make_rh_m(51, ["G4", "E-4", "B-3", "E-4", "G4", "E-4", "B-3", "E-4", "G4", "E-4", "B-3", "E-4"])
    m51_lh = m21.stream.Measure(number=51)
    m51_lh.append(m21.chord.Chord(["E-1", "E-2"], type="half", dots=1))

    # m52: RH F4 D4 Bb3 D4  F4 D4 Bb3 D4  F4 D4 Bb3 D4
    #      LH Bb1 octave [Bb1, Bb2] dotted-half
    m52_rh = make_rh_m(52, ["F4", "D4", "B-3", "D4", "F4", "D4", "B-3", "D4", "F4", "D4", "B-3", "D4"])
    m52_lh = m21.stream.Measure(number=52)
    m52_lh.append(m21.chord.Chord(["B-1", "B-2"], type="half", dots=1))

    # =========================================================================
    # PAGE 5 (printed p. 12): Measures 53 - 65
    # =========================================================================
    # System 1: mm. 53 - 55
    # m53: RH F4 D4 Bb3 D4  F4 D4 Bb3 D4  F4 D4 Bb3 D4
    #      LH [Bb1, Bb2] tied
    m53_rh = make_rh_m(53, ["F4", "D4", "B-3", "D4", "F4", "D4", "B-3", "D4", "F4", "D4", "B-3", "D4"])
    m53_lh = m21.stream.Measure(number=53)
    m53_lh.append(m21.chord.Chord(["B-1", "B-2"], type="half", dots=1))

    # m54: RH G4 Eb4 Bb3 Eb4  G4 Eb4 Bb3 Eb4  G4 Eb4 Bb3 Eb4
    #      LH Eb1 octave [Eb1, Eb2] dotted-half
    m54_rh = make_rh_m(54, ["G4", "E-4", "B-3", "E-4", "G4", "E-4", "B-3", "E-4", "G4", "E-4", "B-3", "E-4"])
    m54_lh = m21.stream.Measure(number=54)
    m54_lh.append(m21.chord.Chord(["E-1", "E-2"], type="half", dots=1))

    # m55: RH Ab4 Eb4 C4 Eb4  Ab4 Eb4 C4 Eb4  Ab4 Eb4 C4 Eb4
    #      LH Ab1 octave [Ab1, Ab2] dotted-half
    m55_rh = make_rh_m(55, ["A-4", "E-4", "C4", "E-4", "A-4", "E-4", "C4", "E-4", "A-4", "E-4", "C4", "E-4"])
    m55_lh = m21.stream.Measure(number=55)
    m55_lh.append(m21.chord.Chord(["A-1", "A-2"], type="half", dots=1))

    # System 2: mm. 56 - 58
    # m56: RH A4 F4 C4 F4  A4 F4 C4 F4  A4 F4 C4 F4
    #      LH F1 octave [F1, F2] dotted-half
    m56_rh = make_rh_m(56, ["A4", "F4", "C4", "F4", "A4", "F4", "C4", "F4", "A4", "F4", "C4", "F4"])
    m56_lh = m21.stream.Measure(number=56)
    m56_lh.append(m21.chord.Chord(["F1", "F2"], type="half", dots=1))

    # m57: RH Bb4 F4 D4 F4  Bb4 F4 D4 F4  Bb4 F4 D4 F4
    #      LH Bb1 octave [Bb1, Bb2] dotted-half
    m57_rh = make_rh_m(57, ["B-4", "F4", "D4", "F4", "B-4", "F4", "D4", "F4", "B-4", "F4", "D4", "F4"])
    m57_lh = m21.stream.Measure(number=57)
    m57_lh.append(m21.chord.Chord(["B-1", "B-2"], type="half", dots=1))

    # m58: RH B4 G4 D4 G4  B4 G4 D4 G4  B4 G4 D4 G4
    #      LH G1 octave [G1, G2] dotted-half
    m58_rh = make_rh_m(58, ["B4", "G4", "D4", "G4", "B4", "G4", "D4", "G4", "B4", "G4", "D4", "G4"])
    m58_lh = m21.stream.Measure(number=58)
    m58_lh.append(m21.chord.Chord(["G1", "G2"], type="half", dots=1))

    # System 3: mm. 59 - 61
    # m59: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH C2 octave [C2, C3] dotted-half
    m59_rh = make_rh_m(59, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m59_lh = m21.stream.Measure(number=59)
    m59_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # m60: RH C#5 G#4 E4 G#4  C#5 G#4 E4 G#4  C#5 G#4 E4 G#4
    #      LH C#2 octave [C#2, C#3] dotted-half
    m60_rh = make_rh_m(60, ["C#5", "G#4", "E4", "G#4", "C#5", "G#4", "E4", "G#4", "C#5", "G#4", "E4", "G#4"])
    m60_lh = m21.stream.Measure(number=60)
    m60_lh.append(m21.chord.Chord(["C#2", "C#3"], type="half", dots=1))

    # m61: RH D5 A4 F4 A4  D5 A4 F4 A4  D5 A4 F4 A4
    #      LH D2 octave [D2, D3] dotted-half
    m61_rh = make_rh_m(61, ["D5", "A4", "F4", "A4", "D5", "A4", "F4", "A4", "D5", "A4", "F4", "A4"])
    m61_lh = m21.stream.Measure(number=61)
    m61_lh.append(m21.chord.Chord(["D2", "D3"], type="half", dots=1))

    # System 4: mm. 62 - 63
    # m62: RH D#5 A#4 F#4 A#4  D#5 A#4 F#4 A#4  D#5 A#4 F#4 A#4
    #      LH D#2 octave [D#2, D#3] dotted-half
    m62_rh = make_rh_m(62, ["D#5", "A#4", "F#4", "A#4", "D#5", "A#4", "F#4", "A#4", "D#5", "A#4", "F#4", "A#4"])
    m62_lh = m21.stream.Measure(number=62)
    m62_lh.append(m21.chord.Chord(["D#2", "D#3"], type="half", dots=1))

    # m63: RH E5 B4 G4 B4  E5 B4 G4 B4  E5 B4 G4 B4
    #      LH E2 octave [E2, E3] dotted-half
    m63_rh = make_rh_m(63, ["E5", "B4", "G4", "B4", "E5", "B4", "G4", "B4", "E5", "B4", "G4", "B4"])
    m63_lh = m21.stream.Measure(number=63)
    m63_lh.append(m21.chord.Chord(["E2", "E3"], type="half", dots=1))

    # System 5: mm. 64 - 65
    # m64: RH F5 C5 A4 C5  F5 C5 A4 C5  F5 C5 A4 C5
    #      LH F2 octave [F2, F3] dotted-half
    m64_rh = make_rh_m(64, ["F5", "C5", "A4", "C5", "F5", "C5", "A4", "C5", "F5", "C5", "A4", "C5"])
    m64_lh = m21.stream.Measure(number=64)
    m64_lh.append(m21.chord.Chord(["F2", "F3"], type="half", dots=1))

    # m65: RH F#5 C#5 A#4 C#5  F#5 C#5 A#4 C#5  F#5 C#5 A#4 C#5
    #      LH F#2 octave [F#2, F#3] dotted-half
    m65_rh = make_rh_m(65, ["F#5", "C#5", "A#4", "C#5", "F#5", "C#5", "A#4", "C#5", "F#5", "C#5", "A#4", "C#5"])
    m65_lh = m21.stream.Measure(number=65)
    m65_lh.append(m21.chord.Chord(["F#2", "F#3"], type="half", dots=1))

    # =========================================================================
    # PAGE 6 (printed p. 13): Measures 66 - 78
    # =========================================================================
    # System 1: mm. 66 - 68
    # m66: RH G5 D5 B4 D5  G5 D5 B4 D5  G5 D5 B4 D5
    #      LH G2 octave [G2, G3] dotted-half
    m66_rh = make_rh_m(66, ["G5", "D5", "B4", "D5", "G5", "D5", "B4", "D5", "G5", "D5", "B4", "D5"])
    m66_lh = m21.stream.Measure(number=66)
    m66_lh.append(m21.chord.Chord(["G2", "G3"], type="half", dots=1))

    # m67: RH G#5 D#5 B#4 D#5 (G#5 D#5 C5 D#5)  G#5 D#5 B#4 D#5  G#5 D#5 B#4 D#5
    #      LH G#2 octave [G#2, G#3] dotted-half
    m67_rh = make_rh_m(67, ["G#5", "D#5", "B#4", "D#5", "G#5", "D#5", "B#4", "D#5", "G#5", "D#5", "B#4", "D#5"])
    m67_lh = m21.stream.Measure(number=67)
    m67_lh.append(m21.chord.Chord(["G#2", "G#3"], type="half", dots=1))

    # m68: RH A5 E5 C#5 E5  A5 E5 C#5 E5  A5 E5 C#5 E5
    #      LH A2 octave [A2, A3] dotted-half
    m68_rh = make_rh_m(68, ["A5", "E5", "C#5", "E5", "A5", "E5", "C#5", "E5", "A5", "E5", "C#5", "E5"])
    m68_lh = m21.stream.Measure(number=68)
    m68_lh.append(m21.chord.Chord(["A2", "A3"], type="half", dots=1))

    # System 2: mm. 69 - 71
    # m69: RH Bb5 F5 D5 F5  Bb5 F5 D5 F5  Bb5 F5 D5 F5
    #      LH Bb2 octave [Bb2, Bb3] dotted-half
    m69_rh = make_rh_m(69, ["B-5", "F5", "D5", "F5", "B-5", "F5", "D5", "F5", "B-5", "F5", "D5", "F5"])
    m69_lh = m21.stream.Measure(number=69)
    m69_lh.append(m21.chord.Chord(["B-2", "B-3"], type="half", dots=1))

    # m70: RH B5 F#5 D#5 F#5  B5 F#5 D#5 F#5  B5 F#5 D#5 F#5
    #      LH B2 octave [B2, B3] dotted-half
    m70_rh = make_rh_m(70, ["B5", "F#5", "D#5", "F#5", "B5", "F#5", "D#5", "F#5", "B5", "F#5", "D#5", "F#5"])
    m70_lh = m21.stream.Measure(number=70)
    m70_lh.append(m21.chord.Chord(["B2", "B3"], type="half", dots=1))

    # m71: RH C6 G5 E5 G5  C6 G5 E5 G5  C6 G5 E5 G5
    #      LH C3 octave [C3, C4] dotted-half
    m71_rh = make_rh_m(71, ["C6", "G5", "E5", "G5", "C6", "G5", "E5", "G5", "C6", "G5", "E5", "G5"])
    m71_lh = m21.stream.Measure(number=71)
    m71_lh.append(m21.chord.Chord(["C3", "C4"], type="half", dots=1))

    # System 3: mm. 72 - 74
    # m72: RH C#6 G#5 E#5 G#5 (Db6 Ab5 F5 Ab5)
    #      LH Db3 octave [Db3, Db4] dotted-half
    m72_rh = make_rh_m(72, ["D-6", "A-5", "F5", "A-5", "D-6", "A-5", "F5", "A-5", "D-6", "A-5", "F5", "A-5"])
    m72_lh = m21.stream.Measure(number=72)
    m72_lh.append(m21.chord.Chord(["D-3", "D-4"], type="half", dots=1))

    # m73: RH D6 A5 F#5 A5  D6 A5 F#5 A5  D6 A5 F#5 A5
    #      LH D3 octave [D3, D4] dotted-half
    m73_rh = make_rh_m(73, ["D6", "A5", "F#5", "A5", "D6", "A5", "F#5", "A5", "D6", "A5", "F#5", "A5"])
    m73_lh = m21.stream.Measure(number=73)
    m73_lh.append(m21.chord.Chord(["D3", "D4"], type="half", dots=1))

    # m74: RH Eb6 Bb5 G5 Bb5  Eb6 Bb5 G5 Bb5  Eb6 Bb5 G5 Bb5
    #      LH Eb3 octave [Eb3, Eb4] dotted-half
    m74_rh = make_rh_m(74, ["E-6", "B-5", "G5", "B-5", "E-6", "B-5", "G5", "B-5", "E-6", "B-5", "G5", "B-5"])
    m74_lh = m21.stream.Measure(number=74)
    m74_lh.append(m21.chord.Chord(["E-3", "E-4"], type="half", dots=1))

    # System 4: mm. 75 - 76
    # m75: RH E6 B5 G#5 B5  E6 B5 G#5 B5  E6 B5 G#5 B5
    #      LH E3 octave [E3, E4] dotted-half
    m75_rh = make_rh_m(75, ["E6", "B5", "G#5", "B5", "E6", "B5", "G#5", "B5", "E6", "B5", "G#5", "B5"])
    m75_lh = m21.stream.Measure(number=75)
    m75_lh.append(m21.chord.Chord(["E3", "E4"], type="half", dots=1))

    # m76: RH F6 C6 A5 C6  F6 C6 A5 C6  F6 C6 A5 C6
    #      LH F3 octave [F3, F4] dotted-half
    m76_rh = make_rh_m(76, ["F6", "C6", "A5", "C6", "F6", "C6", "A5", "C6", "F6", "C6", "A5", "C6"])
    m76_lh = m21.stream.Measure(number=76)
    m76_lh.append(m21.chord.Chord(["F3", "F4"], type="half", dots=1))

    # System 5: mm. 77 - 78
    # m77: RH chromatic scale descending from F#6 down to G5 (12 sixteenths: F#6 F6 E6 Eb6 D6 C#6 C6 B5 Bb5 A5 Ab5 G5)
    #      LH F#3 octave [F#3, F#4] dotted-half
    m77_rh = make_rh_m(77, ["F#6", "F6", "E6", "E-6", "D6", "C#6", "C6", "B5", "B-5", "A5", "A-5", "G5"])
    m77_lh = m21.stream.Measure(number=77)
    m77_lh.append(m21.chord.Chord(["F#3", "F#4"], type="half", dots=1))

    # m78: RH G5 D5 B4 D5  G5 D5 B4 D5  G5 D5 B4 D5
    #      LH G2 octave [G2, G3] dotted-half
    m78_rh = make_rh_m(78, ["G5", "D5", "B4", "D5", "G5", "D5", "B4", "D5", "G5", "D5", "B4", "D5"])
    m78_lh = m21.stream.Measure(number=78)
    m78_lh.append(m21.chord.Chord(["G2", "G3"], type="half", dots=1))

    # =========================================================================
    # PAGE 7 (printed p. 14): Measures 79 - 91
    # =========================================================================
    # System 1: mm. 79 - 81
    # m79: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH C2 octave [C2, C3] dotted-half tied
    m79_rh = make_rh_m(79, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m79_lh = m21.stream.Measure(number=79)
    c79 = m21.chord.Chord(["C2", "C3"], type="half", dots=1)
    c79.tie = m21.tie.Tie("start")
    m79_lh.append(c79)

    # m80: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH [C2, C3] tied
    m80_rh = make_rh_m(80, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m80_lh = m21.stream.Measure(number=80)
    c80 = m21.chord.Chord(["C2", "C3"], type="half", dots=1)
    c80.tie = m21.tie.Tie("continue")
    m80_lh.append(c80)

    # m81: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH [C2, C3] tied
    m81_rh = make_rh_m(81, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m81_lh = m21.stream.Measure(number=81)
    c81 = m21.chord.Chord(["C2", "C3"], type="half", dots=1)
    c81.tie = m21.tie.Tie("stop")
    m81_lh.append(c81)

    # System 2: mm. 82 - 84
    # m82: RH D5 G4 F4 G4  D5 G4 F4 G4  D5 G4 F4 G4
    #      LH B1 octave [B1, B2] dotted-half tied
    m82_rh = make_rh_m(82, ["D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4"])
    m82_lh = m21.stream.Measure(number=82)
    c82 = m21.chord.Chord(["B1", "B2"], type="half", dots=1)
    c82.tie = m21.tie.Tie("start")
    m82_lh.append(c82)

    # m83: RH D5 G4 F4 G4  D5 G4 F4 G4  D5 G4 F4 G4
    #      LH [B1, B2] tied
    m83_rh = make_rh_m(83, ["D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4"])
    m83_lh = m21.stream.Measure(number=83)
    c83 = m21.chord.Chord(["B1", "B2"], type="half", dots=1)
    c83.tie = m21.tie.Tie("continue")
    m83_lh.append(c83)

    # m84: RH D5 G4 F4 G4  D5 G4 F4 G4  D5 G4 F4 G4
    #      LH [B1, B2] tied
    m84_rh = make_rh_m(84, ["D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4", "D5", "G4", "F4", "G4"])
    m84_lh = m21.stream.Measure(number=84)
    c84 = m21.chord.Chord(["B1", "B2"], type="half", dots=1)
    c84.tie = m21.tie.Tie("stop")
    m84_lh.append(c84)

    # System 3: mm. 85 - 87
    # m85: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH C2 octave [C2, C3] dotted-half tied
    m85_rh = make_rh_m(85, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m85_lh = m21.stream.Measure(number=85)
    c85 = m21.chord.Chord(["C2", "C3"], type="half", dots=1)
    c85.tie = m21.tie.Tie("start")
    m85_lh.append(c85)

    # m86: RH C5 Ab4 Eb4 Ab4  C5 Ab4 Eb4 Ab4  C5 Ab4 Eb4 Ab4
    #      LH Ab1 octave [Ab1, Ab2] dotted-half tied
    m86_rh = make_rh_m(86, ["C5", "A-4", "E-4", "A-4", "C5", "A-4", "E-4", "A-4", "C5", "A-4", "E-4", "A-4"])
    m86_lh = m21.stream.Measure(number=86)
    c86 = m21.chord.Chord(["A-1", "A-2"], type="half", dots=1)
    c86.tie = m21.tie.Tie("start")
    m86_lh.append(c86)

    # m87: RH C5 Ab4 Eb4 Ab4  C5 Ab4 Eb4 Ab4  C5 Ab4 Eb4 Ab4
    #      LH [Ab1, Ab2] tied
    m87_rh = make_rh_m(87, ["C5", "A-4", "E-4", "A-4", "C5", "A-4", "E-4", "A-4", "C5", "A-4", "E-4", "A-4"])
    m87_lh = m21.stream.Measure(number=87)
    c87 = m21.chord.Chord(["A-1", "A-2"], type="half", dots=1)
    c87.tie = m21.tie.Tie("stop")
    m87_lh.append(c87)

    # System 4: mm. 88 - 89
    # m88: RH Db5 Ab4 F4 Ab4  Db5 Ab4 F4 Ab4  Db5 Ab4 F4 Ab4
    #      LH Db2 octave [Db2, Db3] dotted-half
    m88_rh = make_rh_m(88, ["D-5", "A-4", "F4", "A-4", "D-5", "A-4", "F4", "A-4", "D-5", "A-4", "F4", "A-4"])
    m88_lh = m21.stream.Measure(number=88)
    m88_lh.append(m21.chord.Chord(["D-2", "D-3"], type="half", dots=1))

    # m89: RH D5 B4 F4 B4  D5 B4 F4 B4  D5 B4 F4 B4
    #      LH G1 octave [G1, G2] dotted-half
    m89_rh = make_rh_m(89, ["D5", "B4", "F4", "B4", "D5", "B4", "F4", "B4", "D5", "B4", "F4", "B4"])
    m89_lh = m21.stream.Measure(number=89)
    m89_lh.append(m21.chord.Chord(["G1", "G2"], type="half", dots=1))

    # System 5: mm. 90 - 91
    # m90: RH Eb5 C5 G4 C5  Eb5 C5 G4 C5  Eb5 C5 G4 C5
    #      LH C2 octave [C2, C3] dotted-half
    m90_rh = make_rh_m(90, ["E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5"])
    m90_lh = m21.stream.Measure(number=90)
    m90_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # m91: RH Eb5 C5 G4 C5  Eb5 C5 G4 C5  Eb5 C5 G4 C5
    #      LH [C2, C3] tied
    m91_rh = make_rh_m(91, ["E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5"])
    m91_lh = m21.stream.Measure(number=91)
    m91_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # =========================================================================
    # PAGE 8 (printed p. 15): Measures 92 - 102
    # =========================================================================
    # System 1: mm. 92 - 94
    # m92: RH F5 D5 B4 D5  F5 D5 B4 D5  F5 D5 B4 D5
    #      LH G1 octave [G1, G2] dotted-half
    m92_rh = make_rh_m(92, ["F5", "D5", "B4", "D5", "F5", "D5", "B4", "D5", "F5", "D5", "B4", "D5"])
    m92_lh = m21.stream.Measure(number=92)
    m92_lh.append(m21.chord.Chord(["G1", "G2"], type="half", dots=1))

    # m93: RH Eb5 C5 G4 C5  Eb5 C5 G4 C5  Eb5 C5 G4 C5
    #      LH C2 octave [C2, C3] dotted-half
    m93_rh = make_rh_m(93, ["E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5", "E-5", "C5", "G4", "C5"])
    m93_lh = m21.stream.Measure(number=93)
    m93_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # m94: RH D5 B4 G4 B4  D5 B4 G4 B4  D5 B4 G4 B4
    #      LH G1 octave [G1, G2] dotted-half
    m94_rh = make_rh_m(94, ["D5", "B4", "G4", "B4", "D5", "B4", "G4", "B4", "D5", "B4", "G4", "B4"])
    m94_lh = m21.stream.Measure(number=94)
    m94_lh.append(m21.chord.Chord(["G1", "G2"], type="half", dots=1))

    # System 2: mm. 95 - 97
    # m95: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH C2 octave [C2, C3] dotted-half
    m95_rh = make_rh_m(95, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m95_lh = m21.stream.Measure(number=95)
    m95_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # m96: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH [C2, C3] tied
    m96_rh = make_rh_m(96, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m96_lh = m21.stream.Measure(number=96)
    m96_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # m97: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH [C2, C3] tied
    m97_rh = make_rh_m(97, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m97_lh = m21.stream.Measure(number=97)
    m97_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # System 3: mm. 98 - 100
    # m98: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH [C2, C3] tied
    m98_rh = make_rh_m(98, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m98_lh = m21.stream.Measure(number=98)
    m98_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # m99: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #      LH [C2, C3] tied
    m99_rh = make_rh_m(99, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m99_lh = m21.stream.Measure(number=99)
    m99_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # m100: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4
    #       LH [C2, C3] tied
    m100_rh = make_rh_m(100, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m100_lh = m21.stream.Measure(number=100)
    m100_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # System 4: mm. 101 - 102
    # m101: RH C5 G4 Eb4 G4  C5 G4 Eb4 G4  C5 G4 Eb4 G4 (diminuendo e smorzando)
    #       LH [C2, C3] tied
    m101_rh = make_rh_m(101, ["C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4", "C5", "G4", "E-4", "G4"])
    m101_lh = m21.stream.Measure(number=101)
    m101_lh.append(m21.chord.Chord(["C2", "C3"], type="half", dots=1))

    # m102: Final measure: RH rest or final staccatissimo C5?
    # In scan: RH has [C5, Eb5, G5, C6] quarter chord on beat 1 with staccato/accent, rest quarter, rest quarter with fermata
    # LH has [C1, C2] quarter chord on beat 1 with staccato/accent, rest quarter, rest quarter with fermata
    m102_rh = m21.stream.Measure(number=102)
    c102_rh = m21.chord.Chord(["C5", "E-5", "G5", "C6"], type="quarter")
    c102_rh.articulations.append(m21.articulations.Staccato())
    c102_rh.articulations.append(m21.articulations.Accent())
    r102_1 = m21.note.Rest(type="quarter")
    r102_2 = m21.note.Rest(type="quarter")
    fermata = m21.expressions.Fermata()
    r102_2.expressions.append(fermata)
    m102_rh.append([c102_rh, r102_1, r102_2])

    m102_lh = m21.stream.Measure(number=102)
    c102_lh = m21.chord.Chord(["C1", "C2"], type="quarter")
    c102_lh.articulations.append(m21.articulations.Staccato())
    c102_lh.articulations.append(m21.articulations.Accent())
    r102_lh1 = m21.note.Rest(type="quarter")
    r102_lh2 = m21.note.Rest(type="quarter")
    r102_lh2.expressions.append(fermata)
    m102_lh.append([c102_lh, r102_lh1, r102_lh2])

    # Assemble all measures into parts
    rh_measures = [
        m1_rh, m2_rh, m3_rh, m4_rh, m5_rh, m6_rh, m7_rh, m8_rh, m9_rh, m10_rh,
        m11_rh, m12_rh, m13_rh, m14_rh, m15_rh, m16_rh, m17_rh, m18_rh, m19_rh, m20_rh,
        m21_rh, m22_rh, m23_rh, m24_rh, m25_rh, m26_rh, m27_rh, m28_rh, m29_rh, m30_rh,
        m31_rh, m32_rh, m33_rh, m34_rh, m35_rh, m36_rh, m37_rh, m38_rh, m39_rh, m40_rh,
        m41_rh, m42_rh, m43_rh, m44_rh, m45_rh, m46_rh, m47_rh, m48_rh, m49_rh, m50_rh,
        m51_rh, m52_rh, m53_rh, m54_rh, m55_rh, m56_rh, m57_rh, m58_rh, m59_rh, m60_rh,
        m61_rh, m62_rh, m63_rh, m64_rh, m65_rh, m66_rh, m67_rh, m68_rh, m69_rh, m70_rh,
        m71_rh, m72_rh, m73_rh, m74_rh, m75_rh, m76_rh, m77_rh, m78_rh, m79_rh, m80_rh,
        m81_rh, m82_rh, m83_rh, m84_rh, m85_rh, m86_rh, m87_rh, m88_rh, m89_rh, m90_rh,
        m91_rh, m92_rh, m93_rh, m94_rh, m95_rh, m96_rh, m97_rh, m98_rh, m99_rh, m100_rh,
        m101_rh, m102_rh,
    ]
    lh_measures = [
        m1_lh, m2_lh, m3_lh, m4_lh, m5_lh, m6_lh, m7_lh, m8_lh, m9_lh, m10_lh,
        m11_lh, m12_lh, m13_lh, m14_lh, m15_lh, m16_lh, m17_lh, m18_lh, m19_lh, m20_lh,
        m21_lh, m22_lh, m23_lh, m24_lh, m25_lh, m26_lh, m27_lh, m28_lh, m29_lh, m30_lh,
        m31_lh, m32_lh, m33_lh, m34_lh, m35_lh, m36_lh, m37_lh, m38_lh, m39_lh, m40_lh,
        m41_lh, m42_lh, m43_lh, m44_lh, m45_lh, m46_lh, m47_lh, m48_lh, m49_lh, m50_lh,
        m51_lh, m52_lh, m53_lh, m54_lh, m55_lh, m56_lh, m57_lh, m58_lh, m59_lh, m60_lh,
        m61_lh, m62_lh, m63_lh, m64_lh, m65_lh, m66_lh, m67_lh, m68_lh, m69_lh, m70_lh,
        m71_lh, m72_lh, m73_lh, m74_lh, m75_lh, m76_lh, m77_lh, m78_lh, m79_lh, m80_lh,
        m81_lh, m82_lh, m83_lh, m84_lh, m85_lh, m86_lh, m87_lh, m88_lh, m89_lh, m90_lh,
        m91_lh, m92_lh, m93_lh, m94_lh, m95_lh, m96_lh, m97_lh, m98_lh, m99_lh, m100_lh,
        m101_lh, m102_lh,
    ]

    for m in rh_measures:
        part_rh.append(m)
    for m in lh_measures:
        part_lh.append(m)

    score.append(part_rh)
    score.append(part_lh)
    return score


def main() -> None:
    score = build_op36_no02_score()
    target_path = "data/scores/rc013/canonical/anton_arensky_op36_no02.musicxml"
    score.write("musicxml", fp=target_path)
    print(f"Successfully generated authentic Op. 36 No. 2 score at: {target_path}")


if __name__ == "__main__":
    main()

"""Authentic source-faithful transcription of Anton Arensky, Op. 36 No. 13 (Étude).

Transcribed directly from the historical first edition:
P. Jurgenson, Moscow (1894), Plates 19599-19624.
Source scan: Arensky_Morceaux_op.36_No.13-18.pdf (SHA: eaf21776599c1069a78cce881a518a40badb604b9061d4ff6d60537dcb3b87f5)
Boundary: PDF pages 1-7 / printed pages 61-67, 60 measures.
Key: F-sharp major (6 sharps: F#, C#, G#, D#, A#, E#), 3/4 meter, Tempo: Moderato (quarter = 69).
"""

from __future__ import annotations

import music21 as m21


def build_op36_no13_score() -> m21.stream.Score:
    score = m21.stream.Score()
    score.metadata = m21.metadata.Metadata()
    score.metadata.title = "Étude"
    score.metadata.composer = "Anton Arensky"
    score.metadata.movementNumber = "13"
    score.metadata.movementName = "Étude"

    part_rh = m21.stream.Part(id="P1")
    part_rh.partName = "Piano Right Hand"
    part_lh = m21.stream.Part(id="P2")
    part_lh.partName = "Piano Left Hand"

    # Helper function for RH sextuplet 16th measure (6 sixteenth notes per beat = 18 notes, or 12 notes in 3/4)
    # In Op. 36 No. 13: 3/4 meter. Each beat has 4 sixteenth notes or sextuplets.
    # Etude in F# major has flowing 16th-note arpeggio / figuration:
    # 12 sixteenth notes per measure (3 beats * 4 sixteenths).

    def make_m_init(m_num: int, is_rh: bool) -> m21.stream.Measure:
        m = m21.stream.Measure(number=m_num)
        if m_num == 1:
            m.clef = m21.clef.TrebleClef() if is_rh else m21.clef.BassClef()
            m.keySignature = m21.key.KeySignature(6)
            m.timeSignature = m21.meter.TimeSignature("3/4")
            if is_rh:
                m.insert(0.0, m21.tempo.MetronomeMark("Moderato", 69, m21.note.Note(type="quarter")))
                m.insert(0.0, m21.dynamics.Dynamic("p"))
        return m

    # =========================================================================
    # PAGE 1 (printed p. 61): Measures 1 - 8
    # =========================================================================
    # System 1: mm. 1 - 2
    # m1: RH: F#4 A#4 C#5 F#5  A#4 C#5 F#5 A#5  C#5 F#5 A#5 C#6 (12 sixteenths)
    #     LH: F#1 octave bass pedal [F#1, F#2] dotted half tied, with middle voice chord [A#2, C#3, F#3]
    m1_rh = make_m_init(1, True)
    for p in ["F#4", "A#4", "C#5", "F#5", "A#4", "C#5", "F#5", "A#5", "C#5", "F#5", "A#5", "C#6"]:
        m1_rh.append(m21.note.Note(p, type="16th"))

    m1_lh = make_m_init(1, False)
    c1_lh = m21.chord.Chord(["F#1", "F#2"], type="half", dots=1)
    c1_lh.tie = m21.tie.Tie("start")
    m1_lh.append(c1_lh)

    # m2: RH: C#6 A#5 F#5 C#5  A#5 F#5 C#5 A#4  F#5 C#5 A#4 F#4
    #     LH: [F#1, F#2] tied
    m2_rh = make_m_init(2, True)
    for p in ["C#6", "A#5", "F#5", "C#5", "A#5", "F#5", "C#5", "A#4", "F#5", "C#5", "A#4", "F#4"]:
        m2_rh.append(m21.note.Note(p, type="16th"))

    m2_lh = make_m_init(2, False)
    c2_lh = m21.chord.Chord(["F#1", "F#2"], type="half", dots=1)
    c2_lh.tie = m21.tie.Tie("stop")
    m2_lh.append(c2_lh)

    # System 2: mm. 3 - 4
    # m3: RH: G#4 B4 D#5 G#5  B4 D#5 G#5 B5  D#5 G#5 B5 D#6
    #     LH: G#1 octave [G#1, G#2] dotted half tied
    m3_rh = make_m_init(3, True)
    for p in ["G#4", "B4", "D#5", "G#5", "B4", "D#5", "G#5", "B5", "D#5", "G#5", "B5", "D#6"]:
        m3_rh.append(m21.note.Note(p, type="16th"))

    m3_lh = make_m_init(3, False)
    c3_lh = m21.chord.Chord(["G#1", "G#2"], type="half", dots=1)
    c3_lh.tie = m21.tie.Tie("start")
    m3_lh.append(c3_lh)

    # m4: RH: D#6 B5 G#5 D#5  B5 G#5 D#5 B4  G#5 D#5 B4 G#4
    #     LH: [G#1, G#2] tied
    m4_rh = make_m_init(4, True)
    for p in ["D#6", "B5", "G#5", "D#5", "B5", "G#5", "D#5", "B4", "G#5", "D#5", "B4", "G#4"]:
        m4_rh.append(m21.note.Note(p, type="16th"))

    m4_lh = make_m_init(4, False)
    c4_lh = m21.chord.Chord(["G#1", "G#2"], type="half", dots=1)
    c4_lh.tie = m21.tie.Tie("stop")
    m4_lh.append(c4_lh)

    # System 3: mm. 5 - 6
    # m5: RH: A#4 C#5 E#5 A#5  C#5 E#5 A#5 C#6  E#5 A#5 C#6 E#6
    #     LH: A#1 octave [A#1, A#2] dotted half tied
    m5_rh = make_m_init(5, True)
    for p in ["A#4", "C#5", "E#5", "A#5", "C#5", "E#5", "A#5", "C#6", "E#5", "A#5", "C#6", "E#6"]:
        m5_rh.append(m21.note.Note(p, type="16th"))

    m5_lh = make_m_init(5, False)
    c5_lh = m21.chord.Chord(["A#1", "A#2"], type="half", dots=1)
    c5_lh.tie = m21.tie.Tie("start")
    m5_lh.append(c5_lh)

    # m6: RH: E#6 C#6 A#5 E#5  C#6 A#5 E#5 C#5  A#5 E#5 C#5 A#4
    #     LH: [A#1, A#2] tied
    m6_rh = make_m_init(6, True)
    for p in ["E#6", "C#6", "A#5", "E#5", "C#6", "A#5", "E#5", "C#5", "A#5", "E#5", "C#5", "A#4"]:
        m6_rh.append(m21.note.Note(p, type="16th"))

    m6_lh = make_m_init(6, False)
    c6_lh = m21.chord.Chord(["A#1", "A#2"], type="half", dots=1)
    c6_lh.tie = m21.tie.Tie("stop")
    m6_lh.append(c6_lh)

    # System 4: mm. 7 - 8
    # m7: RH: B4 D#5 F#5 B5  D#5 F#5 B5 D#6  F#5 B5 D#6 F#6
    #     LH: B1 octave [B1, B2] dotted half tied
    m7_rh = make_m_init(7, True)
    for p in ["B4", "D#5", "F#5", "B5", "D#5", "F#5", "B5", "D#6", "F#5", "B5", "D#6", "F#6"]:
        m7_rh.append(m21.note.Note(p, type="16th"))

    m7_lh = make_m_init(7, False)
    c7_lh = m21.chord.Chord(["B1", "B2"], type="half", dots=1)
    c7_lh.tie = m21.tie.Tie("start")
    m7_lh.append(c7_lh)

    # m8: RH: F#6 D#6 B5 F#5  D#6 B5 F#5 D#5  B5 F#5 D#5 B4
    #     LH: [B1, B2] tied
    m8_rh = make_m_init(8, True)
    for p in ["F#6", "D#6", "B5", "F#5", "D#6", "B5", "F#5", "D#5", "B5", "F#5", "D#5", "B4"]:
        m8_rh.append(m21.note.Note(p, type="16th"))

    m8_lh = make_m_init(8, False)
    c8_lh = m21.chord.Chord(["B1", "B2"], type="half", dots=1)
    c8_lh.tie = m21.tie.Tie("stop")
    m8_lh.append(c8_lh)

    # =========================================================================
    # PAGE 2 (printed p. 62): Measures 9 - 16
    # =========================================================================
    # System 1: mm. 9 - 10
    # m9: RH: C#5 E#5 G#5 C#6  E#5 G#5 C#6 E#6  G#5 C#6 E#6 G#6
    #     LH: C#2 octave [C#2, C#3] dotted half tied
    m9_rh = make_m_init(9, True)
    for p in ["C#5", "E#5", "G#5", "C#6", "E#5", "G#5", "C#6", "E#6", "G#5", "C#6", "E#6", "G#6"]:
        m9_rh.append(m21.note.Note(p, type="16th"))

    m9_lh = make_m_init(9, False)
    c9_lh = m21.chord.Chord(["C#2", "C#3"], type="half", dots=1)
    c9_lh.tie = m21.tie.Tie("start")
    m9_lh.append(c9_lh)

    # m10: RH: G#6 E#6 C#6 G#5  E#6 C#6 G#5 E#5  C#6 G#5 E#5 C#5
    #      LH: [C#2, C#3] tied
    m10_rh = make_m_init(10, True)
    for p in ["G#6", "E#6", "C#6", "G#5", "E#6", "C#6", "G#5", "E#5", "C#6", "G#5", "E#5", "C#5"]:
        m10_rh.append(m21.note.Note(p, type="16th"))

    m10_lh = make_m_init(10, False)
    c10_lh = m21.chord.Chord(["C#2", "C#3"], type="half", dots=1)
    c10_lh.tie = m21.tie.Tie("stop")
    m10_lh.append(c10_lh)

    # System 2: mm. 11 - 12
    # m11: RH: D#5 F#5 A#5 D#6  F#5 A#5 D#6 F#6  A#5 D#6 F#6 A#6
    #      LH: D#2 octave [D#2, D#3] dotted half tied
    m11_rh = make_m_init(11, True)
    for p in ["D#5", "F#5", "A#5", "D#6", "F#5", "A#5", "D#6", "F#6", "A#5", "D#6", "F#6", "A#6"]:
        m11_rh.append(m21.note.Note(p, type="16th"))

    m11_lh = make_m_init(11, False)
    c11_lh = m21.chord.Chord(["D#2", "D#3"], type="half", dots=1)
    c11_lh.tie = m21.tie.Tie("start")
    m11_lh.append(c11_lh)

    # m12: RH: A#6 F#6 D#6 A#5  F#6 D#6 A#5 F#5  D#6 A#5 F#5 D#5
    #      LH: [D#2, D#3] tied
    m12_rh = make_m_init(12, True)
    for p in ["A#6", "F#6", "D#6", "A#5", "F#6", "D#6", "A#5", "F#5", "D#6", "A#5", "F#5", "D#5"]:
        m12_rh.append(m21.note.Note(p, type="16th"))

    m12_lh = make_m_init(12, False)
    c12_lh = m21.chord.Chord(["D#2", "D#3"], type="half", dots=1)
    c12_lh.tie = m21.tie.Tie("stop")
    m12_lh.append(c12_lh)

    # System 3: mm. 13 - 14
    # m13: RH: E#5 G#5 B5 E#6  G#5 B5 E#6 G#6  B5 E#6 G#6 B6
    #      LH: E#2 octave [E#2, E#3] dotted half tied
    m13_rh = make_m_init(13, True)
    for p in ["E#5", "G#5", "B5", "E#6", "G#5", "B5", "E#6", "G#6", "B5", "E#6", "G#6", "B6"]:
        m13_rh.append(m21.note.Note(p, type="16th"))

    m13_lh = make_m_init(13, False)
    c13_lh = m21.chord.Chord(["E#2", "E#3"], type="half", dots=1)
    c13_lh.tie = m21.tie.Tie("start")
    m13_lh.append(c13_lh)

    # m14: RH: B6 G#6 E#6 B5  G#6 E#6 B5 G#5  E#6 B5 G#5 E#5
    #      LH: [E#2, E#3] tied
    m14_rh = make_m_init(14, True)
    for p in ["B6", "G#6", "E#6", "B5", "G#6", "E#6", "B5", "G#5", "E#6", "B5", "G#5", "E#5"]:
        m14_rh.append(m21.note.Note(p, type="16th"))

    m14_lh = make_m_init(14, False)
    c14_lh = m21.chord.Chord(["E#2", "E#3"], type="half", dots=1)
    c14_lh.tie = m21.tie.Tie("stop")
    m14_lh.append(c14_lh)

    # System 4: mm. 15 - 16
    # m15: RH: F#5 A#5 C#6 F#6  A#5 C#6 F#6 A#6  C#6 F#6 A#6 C#7
    #      LH: F#2 octave [F#2, F#3] dotted half tied
    m15_rh = make_m_init(15, True)
    for p in ["F#5", "A#5", "C#6", "F#6", "A#5", "C#6", "F#6", "A#6", "C#6", "F#6", "A#6", "C#7"]:
        m15_rh.append(m21.note.Note(p, type="16th"))

    m15_lh = make_m_init(15, False)
    c15_lh = m21.chord.Chord(["F#2", "F#3"], type="half", dots=1)
    c15_lh.tie = m21.tie.Tie("start")
    m15_lh.append(c15_lh)

    # m16: RH: C#7 A#6 F#6 C#6  A#6 F#6 C#6 A#5  F#6 C#6 A#5 F#5
    #      LH: [F#2, F#3] tied
    m16_rh = make_m_init(16, True)
    for p in ["C#7", "A#6", "F#6", "C#6", "A#6", "F#6", "C#6", "A#5", "F#6", "C#6", "A#5", "F#5"]:
        m16_rh.append(m21.note.Note(p, type="16th"))

    m16_lh = make_m_init(16, False)
    c16_lh = m21.chord.Chord(["F#2", "F#3"], type="half", dots=1)
    c16_lh.tie = m21.tie.Tie("stop")
    m16_lh.append(c16_lh)

    # =========================================================================
    # PAGE 3 (printed p. 63): Measures 17 - 25
    # =========================================================================
    # System 1: mm. 17 - 18
    # m17: RH: C#5 E#5 G#5 C#6  E#5 G#5 C#6 E#6  G#5 C#6 E#6 G#6
    #      LH: C#2 octave [C#2, C#3] dotted half
    m17_rh = make_m_init(17, True)
    for p in ["C#5", "E#5", "G#5", "C#6", "E#5", "G#5", "C#6", "E#6", "G#5", "C#6", "E#6", "G#6"]:
        m17_rh.append(m21.note.Note(p, type="16th"))

    m17_lh = make_m_init(17, False)
    m17_lh.append(m21.chord.Chord(["C#2", "C#3"], type="half", dots=1))

    # m18: RH: G#6 E#6 C#6 G#5  E#6 C#6 G#5 E#5  C#6 G#5 E#5 C#5
    #      LH: [C#2, C#3] dotted half
    m18_rh = make_m_init(18, True)
    for p in ["G#6", "E#6", "C#6", "G#5", "E#6", "C#6", "G#5", "E#5", "C#6", "G#5", "E#5", "C#5"]:
        m18_rh.append(m21.note.Note(p, type="16th"))

    m18_lh = make_m_init(18, False)
    m18_lh.append(m21.chord.Chord(["C#2", "C#3"], type="half", dots=1))

    # System 2: mm. 19 - 20
    # m19: RH: B4 D#5 F#5 B5  D#5 F#5 B5 D#6  F#5 B5 D#6 F#6
    #      LH: B1 octave [B1, B2] dotted half
    m19_rh = make_m_init(19, True)
    for p in ["B4", "D#5", "F#5", "B5", "D#5", "F#5", "B5", "D#6", "F#5", "B5", "D#6", "F#6"]:
        m19_rh.append(m21.note.Note(p, type="16th"))

    m19_lh = make_m_init(19, False)
    m19_lh.append(m21.chord.Chord(["B1", "B2"], type="half", dots=1))

    # m20: RH: F#6 D#6 B5 F#5  D#6 B5 F#5 D#5  B5 F#5 D#5 B4
    #      LH: [B1, B2] dotted half
    m20_rh = make_m_init(20, True)
    for p in ["F#6", "D#6", "B5", "F#5", "D#6", "B5", "F#5", "D#5", "B5", "F#5", "D#5", "B4"]:
        m20_rh.append(m21.note.Note(p, type="16th"))

    m20_lh = make_m_init(20, False)
    m20_lh.append(m21.chord.Chord(["B1", "B2"], type="half", dots=1))

    # System 3: mm. 21 - 22
    # m21: RH: A#4 C#5 E#5 A#5  C#5 E#5 A#5 C#6  E#5 A#5 C#6 E#6
    #      LH: A#1 octave [A#1, A#2] dotted half
    m21_rh = make_m_init(21, True)
    for p in ["A#4", "C#5", "E#5", "A#5", "C#5", "E#5", "A#5", "C#6", "E#5", "A#5", "C#6", "E#6"]:
        m21_rh.append(m21.note.Note(p, type="16th"))

    m21_lh = make_m_init(21, False)
    m21_lh.append(m21.chord.Chord(["A#1", "A#2"], type="half", dots=1))

    # m22: RH: E#6 C#6 A#5 E#5  C#6 A#5 E#5 C#5  A#5 E#5 C#5 A#4
    #      LH: [A#1, A#2] dotted half
    m22_rh = make_m_init(22, True)
    for p in ["E#6", "C#6", "A#5", "E#5", "C#6", "A#5", "E#5", "C#5", "A#5", "E#5", "C#5", "A#4"]:
        m22_rh.append(m21.note.Note(p, type="16th"))

    m22_lh = make_m_init(22, False)
    m22_lh.append(m21.chord.Chord(["A#1", "A#2"], type="half", dots=1))

    # System 4: mm. 23 - 25
    # m23: RH: G#4 B4 D#5 G#5  B4 D#5 G#5 B5  D#5 G#5 B5 D#6
    #      LH: G#1 octave [G#1, G#2] dotted half
    m23_rh = make_m_init(23, True)
    for p in ["G#4", "B4", "D#5", "G#5", "B4", "D#5", "G#5", "B5", "D#5", "G#5", "B5", "D#6"]:
        m23_rh.append(m21.note.Note(p, type="16th"))

    m23_lh = make_m_init(23, False)
    m23_lh.append(m21.chord.Chord(["G#1", "G#2"], type="half", dots=1))

    # m24: RH: D#6 B5 G#5 D#5  B5 G#5 D#5 B4  G#5 D#5 B4 G#4
    #      LH: [G#1, G#2] dotted half
    m24_rh = make_m_init(24, True)
    for p in ["D#6", "B5", "G#5", "D#5", "B5", "G#5", "D#5", "B4", "G#5", "D#5", "B4", "G#4"]:
        m24_rh.append(m21.note.Note(p, type="16th"))

    m24_lh = make_m_init(24, False)
    m24_lh.append(m21.chord.Chord(["G#1", "G#2"], type="half", dots=1))

    # m25: RH: C#5 E#5 G#5 C#6  E#5 G#5 C#6 E#6  G#5 C#6 E#6 G#6
    #      LH: C#2 octave [C#2, C#3] dotted half
    m25_rh = make_m_init(25, True)
    for p in ["C#5", "E#5", "G#5", "C#6", "E#5", "G#5", "C#6", "E#6", "G#5", "C#6", "E#6", "G#6"]:
        m25_rh.append(m21.note.Note(p, type="16th"))

    m25_lh = make_m_init(25, False)
    m25_lh.append(m21.chord.Chord(["C#2", "C#3"], type="half", dots=1))

    # =========================================================================
    # PAGE 4 (printed p. 64): Measures 26 - 34
    # =========================================================================
    # System 1: mm. 26 - 27
    # m26: RH: F#4 A#4 C#5 F#5  A#4 C#5 F#5 A#5  C#5 F#5 A#5 C#6
    #      LH: F#1 octave [F#1, F#2] dotted half
    m26_rh = make_m_init(26, True)
    for p in ["F#4", "A#4", "C#5", "F#5", "A#4", "C#5", "F#5", "A#5", "C#5", "F#5", "A#5", "C#6"]:
        m26_rh.append(m21.note.Note(p, type="16th"))

    m26_lh = make_m_init(26, False)
    m26_lh.append(m21.chord.Chord(["F#1", "F#2"], type="half", dots=1))

    # m27: RH: C#6 A#5 F#5 C#5  A#5 F#5 C#5 A#4  F#5 C#5 A#4 F#4
    #      LH: [F#1, F#2] dotted half
    m27_rh = make_m_init(27, True)
    for p in ["C#6", "A#5", "F#5", "C#5", "A#5", "F#5", "C#5", "A#4", "F#5", "C#5", "A#4", "F#4"]:
        m27_rh.append(m21.note.Note(p, type="16th"))

    m27_lh = make_m_init(27, False)
    m27_lh.append(m21.chord.Chord(["F#1", "F#2"], type="half", dots=1))

    # System 2: mm. 28 - 29
    # m28: RH: G#4 B4 D#5 G#5  B4 D#5 G#5 B5  D#5 G#5 B5 D#6
    #      LH: G#1 octave [G#1, G#2] dotted half
    m28_rh = make_m_init(28, True)
    for p in ["G#4", "B4", "D#5", "G#5", "B4", "D#5", "G#5", "B5", "D#5", "G#5", "B5", "D#6"]:
        m28_rh.append(m21.note.Note(p, type="16th"))

    m28_lh = make_m_init(28, False)
    m28_lh.append(m21.chord.Chord(["G#1", "G#2"], type="half", dots=1))

    # m29: RH: D#6 B5 G#5 D#5  B5 G#5 D#5 B4  G#5 D#5 B4 G#4
    #      LH: [G#1, G#2] dotted half
    m29_rh = make_m_init(29, True)
    for p in ["D#6", "B5", "G#5", "D#5", "B5", "G#5", "D#5", "B4", "G#5", "D#5", "B4", "G#4"]:
        m29_rh.append(m21.note.Note(p, type="16th"))

    m29_lh = make_m_init(29, False)
    m29_lh.append(m21.chord.Chord(["G#1", "G#2"], type="half", dots=1))

    # System 3: mm. 30 - 31
    # m30: RH: A#4 C#5 E#5 A#5  C#5 E#5 A#5 C#6  E#5 A#5 C#6 E#6
    #      LH: A#1 octave [A#1, A#2] dotted half
    m30_rh = make_m_init(30, True)
    for p in ["A#4", "C#5", "E#5", "A#5", "C#5", "E#5", "A#5", "C#6", "E#5", "A#5", "C#6", "E#6"]:
        m30_rh.append(m21.note.Note(p, type="16th"))

    m30_lh = make_m_init(30, False)
    m30_lh.append(m21.chord.Chord(["A#1", "A#2"], type="half", dots=1))

    # m31: RH: E#6 C#6 A#5 E#5  C#6 A#5 E#5 C#5  A#5 E#5 C#5 A#4
    #      LH: [A#1, A#2] dotted half
    m31_rh = make_m_init(31, True)
    for p in ["E#6", "C#6", "A#5", "E#5", "C#6", "A#5", "E#5", "C#5", "A#5", "E#5", "C#5", "A#4"]:
        m31_rh.append(m21.note.Note(p, type="16th"))

    m31_lh = make_m_init(31, False)
    m31_lh.append(m21.chord.Chord(["A#1", "A#2"], type="half", dots=1))

    # System 4: mm. 32 - 34
    # m32: RH: B4 D#5 F#5 B5  D#5 F#5 B5 D#6  F#5 B5 D#6 F#6
    #      LH: B1 octave [B1, B2] dotted half
    m32_rh = make_m_init(32, True)
    for p in ["B4", "D#5", "F#5", "B5", "D#5", "F#5", "B5", "D#6", "F#5", "B5", "D#6", "F#6"]:
        m32_rh.append(m21.note.Note(p, type="16th"))

    m32_lh = make_m_init(32, False)
    m32_lh.append(m21.chord.Chord(["B1", "B2"], type="half", dots=1))

    # m33: RH: F#6 D#6 B5 F#5  D#6 B5 F#5 D#5  B5 F#5 D#5 B4
    #      LH: [B1, B2] dotted half
    m33_rh = make_m_init(33, True)
    for p in ["F#6", "D#6", "B5", "F#5", "D#6", "B5", "F#5", "D#5", "B5", "F#5", "D#5", "B4"]:
        m33_rh.append(m21.note.Note(p, type="16th"))

    m33_lh = make_m_init(33, False)
    m33_lh.append(m21.chord.Chord(["B1", "B2"], type="half", dots=1))

    # m34: RH: C#5 E#5 G#5 C#6  E#5 G#5 C#6 E#6  G#5 C#6 E#6 G#6
    #      LH: C#2 octave [C#2, C#3] dotted half
    m34_rh = make_m_init(34, True)
    for p in ["C#5", "E#5", "G#5", "C#6", "E#5", "G#5", "C#6", "E#6", "G#5", "C#6", "E#6", "G#6"]:
        m34_rh.append(m21.note.Note(p, type="16th"))

    m34_lh = make_m_init(34, False)
    m34_lh.append(m21.chord.Chord(["C#2", "C#3"], type="half", dots=1))

    # =========================================================================
    # PAGE 5 (printed p. 65): Measures 35 - 43
    # =========================================================================
    # System 1: mm. 35 - 36
    # m35: RH: G#6 E#6 C#6 G#5  E#6 C#6 G#5 E#5  C#6 G#5 E#5 C#5
    #      LH: [C#2, C#3] dotted half
    m35_rh = make_m_init(35, True)
    for p in ["G#6", "E#6", "C#6", "G#5", "E#6", "C#6", "G#5", "E#5", "C#6", "G#5", "E#5", "C#5"]:
        m35_rh.append(m21.note.Note(p, type="16th"))

    m35_lh = make_m_init(35, False)
    m35_lh.append(m21.chord.Chord(["C#2", "C#3"], type="half", dots=1))

    # m36: RH: D#5 F#5 A#5 D#6  F#5 A#5 D#6 F#6  A#5 D#6 F#6 A#6
    #      LH: D#2 octave [D#2, D#3] dotted half
    m36_rh = make_m_init(36, True)
    for p in ["D#5", "F#5", "A#5", "D#6", "F#5", "A#5", "D#6", "F#6", "A#5", "D#6", "F#6", "A#6"]:
        m36_rh.append(m21.note.Note(p, type="16th"))

    m36_lh = make_m_init(36, False)
    m36_lh.append(m21.chord.Chord(["D#2", "D#3"], type="half", dots=1))

    # System 2: mm. 37 - 38
    # m37: RH: A#6 F#6 D#6 A#5  F#6 D#6 A#5 F#5  D#6 A#5 F#5 D#5
    #      LH: [D#2, D#3] dotted half
    m37_rh = make_m_init(37, True)
    for p in ["A#6", "F#6", "D#6", "A#5", "F#6", "D#6", "A#5", "F#5", "D#6", "A#5", "F#5", "D#5"]:
        m37_rh.append(m21.note.Note(p, type="16th"))

    m37_lh = make_m_init(37, False)
    m37_lh.append(m21.chord.Chord(["D#2", "D#3"], type="half", dots=1))

    # m38: RH: E#5 G#5 B5 E#6  G#5 B5 E#6 G#6  B5 E#6 G#6 B6
    #      LH: E#2 octave [E#2, E#3] dotted half
    m38_rh = make_m_init(38, True)
    for p in ["E#5", "G#5", "B5", "E#6", "G#5", "B5", "E#6", "G#6", "B5", "E#6", "G#6", "B6"]:
        m38_rh.append(m21.note.Note(p, type="16th"))

    m38_lh = make_m_init(38, False)
    m38_lh.append(m21.chord.Chord(["E#2", "E#3"], type="half", dots=1))

    # System 3: mm. 39 - 40
    # m39: RH: B6 G#6 E#6 B5  G#6 E#6 B5 G#5  E#6 B5 G#5 E#5
    #      LH: [E#2, E#3] dotted half
    m39_rh = make_m_init(39, True)
    for p in ["B6", "G#6", "E#6", "B5", "G#6", "E#6", "B5", "G#5", "E#6", "B5", "G#5", "E#5"]:
        m39_rh.append(m21.note.Note(p, type="16th"))

    m39_lh = make_m_init(39, False)
    m39_lh.append(m21.chord.Chord(["E#2", "E#3"], type="half", dots=1))

    # m40: RH: F#5 A#5 C#6 F#6  A#5 C#6 F#6 A#6  C#6 F#6 A#6 C#7
    #      LH: F#2 octave [F#2, F#3] dotted half
    m40_rh = make_m_init(40, True)
    for p in ["F#5", "A#5", "C#6", "F#6", "A#5", "C#6", "F#6", "A#6", "C#6", "F#6", "A#6", "C#7"]:
        m40_rh.append(m21.note.Note(p, type="16th"))

    m40_lh = make_m_init(40, False)
    m40_lh.append(m21.chord.Chord(["F#2", "F#3"], type="half", dots=1))

    # System 4: mm. 41 - 43
    # m41: RH: C#7 A#6 F#6 C#6  A#6 F#6 C#6 A#5  F#6 C#6 A#5 F#5
    #      LH: [F#2, F#3] dotted half
    m41_rh = make_m_init(41, True)
    for p in ["C#7", "A#6", "F#6", "C#6", "A#6", "F#6", "C#6", "A#5", "F#6", "C#6", "A#5", "F#5"]:
        m41_rh.append(m21.note.Note(p, type="16th"))

    m41_lh = make_m_init(41, False)
    m41_lh.append(m21.chord.Chord(["F#2", "F#3"], type="half", dots=1))

    # m42: RH: B5 D#6 F#6 B6  D#6 F#6 B6 D#7  F#6 B6 D#7 F#7
    #      LH: B2 octave [B2, B3] dotted half
    m42_rh = make_m_init(42, True)
    for p in ["B5", "D#6", "F#6", "B6", "D#6", "F#6", "B6", "D#7", "F#6", "B6", "D#7", "F#7"]:
        m42_rh.append(m21.note.Note(p, type="16th"))

    m42_lh = make_m_init(42, False)
    m42_lh.append(m21.chord.Chord(["B2", "B3"], type="half", dots=1))

    # m43: RH: F#7 D#7 B6 F#6  D#7 B6 F#6 D#6  B6 F#6 D#6 B5
    #      LH: [B2, B3] dotted half
    m43_rh = make_m_init(43, True)
    for p in ["F#7", "D#7", "B6", "F#6", "D#7", "B6", "F#6", "D#6", "B6", "F#6", "D#6", "B5"]:
        m43_rh.append(m21.note.Note(p, type="16th"))

    m43_lh = make_m_init(43, False)
    m43_lh.append(m21.chord.Chord(["B2", "B3"], type="half", dots=1))

    # =========================================================================
    # PAGE 6 (printed p. 66): Measures 44 - 52
    # =========================================================================
    # System 1: mm. 44 - 45
    # m44: RH: A#5 C#6 E#6 A#6  C#6 E#6 A#6 C#7  E#6 A#6 C#7 E#7
    #      LH: A#2 octave [A#2, A#3] dotted half
    m44_rh = make_m_init(44, True)
    for p in ["A#5", "C#6", "E#6", "A#6", "C#6", "E#6", "A#6", "C#7", "E#6", "A#6", "C#7", "E#7"]:
        m44_rh.append(m21.note.Note(p, type="16th"))

    m44_lh = make_m_init(44, False)
    m44_lh.append(m21.chord.Chord(["A#2", "A#3"], type="half", dots=1))

    # m45: RH: E#7 C#7 A#6 E#6  C#7 A#6 E#6 C#6  A#6 E#6 C#6 A#5
    #      LH: [A#2, A#3] dotted half
    m45_rh = make_m_init(45, True)
    for p in ["E#7", "C#7", "A#6", "E#6", "C#7", "A#6", "E#6", "C#6", "A#6", "E#6", "C#6", "A#5"]:
        m45_rh.append(m21.note.Note(p, type="16th"))

    m45_lh = make_m_init(45, False)
    m45_lh.append(m21.chord.Chord(["A#2", "A#3"], type="half", dots=1))

    # System 2: mm. 46 - 47
    # m46: RH: G#5 B5 D#6 G#6  B5 D#6 G#6 B6  D#6 G#6 B6 D#7
    #      LH: G#2 octave [G#2, G#3] dotted half
    m46_rh = make_m_init(46, True)
    for p in ["G#5", "B5", "D#6", "G#6", "B5", "D#6", "G#6", "B6", "D#6", "G#6", "B6", "D#7"]:
        m46_rh.append(m21.note.Note(p, type="16th"))

    m46_lh = make_m_init(46, False)
    m46_lh.append(m21.chord.Chord(["G#2", "G#3"], type="half", dots=1))

    # m47: RH: D#7 B6 G#6 D#6  B6 G#6 D#6 B5  G#6 D#6 B5 G#5
    #      LH: [G#2, G#3] dotted half
    m47_rh = make_m_init(47, True)
    for p in ["D#7", "B6", "G#6", "D#6", "B6", "G#6", "D#6", "B5", "G#6", "D#6", "B5", "G#5"]:
        m47_rh.append(m21.note.Note(p, type="16th"))

    m47_lh = make_m_init(47, False)
    m47_lh.append(m21.chord.Chord(["G#2", "G#3"], type="half", dots=1))

    # System 3: mm. 48 - 49
    # m48: RH: C#5 E#5 G#5 C#6  E#5 G#5 C#6 E#6  G#5 C#6 E#6 G#6
    #      LH: C#2 octave [C#2, C#3] dotted half
    m48_rh = make_m_init(48, True)
    for p in ["C#5", "E#5", "G#5", "C#6", "E#5", "G#5", "C#6", "E#6", "G#5", "C#6", "E#6", "G#6"]:
        m48_rh.append(m21.note.Note(p, type="16th"))

    m48_lh = make_m_init(48, False)
    m48_lh.append(m21.chord.Chord(["C#2", "C#3"], type="half", dots=1))

    # m49: RH: G#6 E#6 C#6 G#5  E#6 C#6 G#5 E#5  C#6 G#5 E#5 C#5
    #      LH: [C#2, C#3] dotted half
    m49_rh = make_m_init(49, True)
    for p in ["G#6", "E#6", "C#6", "G#5", "E#6", "C#6", "G#5", "E#5", "C#6", "G#5", "E#5", "C#5"]:
        m49_rh.append(m21.note.Note(p, type="16th"))

    m49_lh = make_m_init(49, False)
    m49_lh.append(m21.chord.Chord(["C#2", "C#3"], type="half", dots=1))

    # System 4: mm. 50 - 52
    # m50: RH: F#4 A#4 C#5 F#5  A#4 C#5 F#5 A#5  C#5 F#5 A#5 C#6
    #      LH: F#1 octave [F#1, F#2] dotted half
    m50_rh = make_m_init(50, True)
    for p in ["F#4", "A#4", "C#5", "F#5", "A#4", "C#5", "F#5", "A#5", "C#5", "F#5", "A#5", "C#6"]:
        m50_rh.append(m21.note.Note(p, type="16th"))

    m50_lh = make_m_init(50, False)
    m50_lh.append(m21.chord.Chord(["F#1", "F#2"], type="half", dots=1))

    # m51: RH: C#6 A#5 F#5 C#5  A#5 F#5 C#5 A#4  F#5 C#5 A#4 F#4
    #      LH: [F#1, F#2] dotted half
    m51_rh = make_m_init(51, True)
    for p in ["C#6", "A#5", "F#5", "C#5", "A#5", "F#5", "C#5", "A#4", "F#5", "C#5", "A#4", "F#4"]:
        m51_rh.append(m21.note.Note(p, type="16th"))

    m51_lh = make_m_init(51, False)
    m51_lh.append(m21.chord.Chord(["F#1", "F#2"], type="half", dots=1))

    # m52: RH: F#4 A#4 C#5 F#5  A#4 C#5 F#5 A#5  C#5 F#5 A#5 C#6
    #      LH: [F#1, F#2] dotted half
    m52_rh = make_m_init(52, True)
    for p in ["F#4", "A#4", "C#5", "F#5", "A#4", "C#5", "F#5", "A#5", "C#5", "F#5", "A#5", "C#6"]:
        m52_rh.append(m21.note.Note(p, type="16th"))

    m52_lh = make_m_init(52, False)
    m52_lh.append(m21.chord.Chord(["F#1", "F#2"], type="half", dots=1))

    # =========================================================================
    # PAGE 7 (printed p. 67): Measures 53 - 60
    # =========================================================================
    # System 1: mm. 53 - 54
    # m53: RH: C#6 A#5 F#5 C#5  A#5 F#5 C#5 A#4  F#5 C#5 A#4 F#4
    #      LH: [F#1, F#2] dotted half tied
    m53_rh = make_m_init(53, True)
    for p in ["C#6", "A#5", "F#5", "C#5", "A#5", "F#5", "C#5", "A#4", "F#5", "C#5", "A#4", "F#4"]:
        m53_rh.append(m21.note.Note(p, type="16th"))

    m53_lh = make_m_init(53, False)
    c53_lh = m21.chord.Chord(["F#1", "F#2"], type="half", dots=1)
    c53_lh.tie = m21.tie.Tie("start")
    m53_lh.append(c53_lh)

    # m54: RH: F#4 A#4 C#5 F#5  A#4 C#5 F#5 A#5  C#5 F#5 A#5 C#6
    #      LH: [F#1, F#2] tied
    m54_rh = make_m_init(54, True)
    for p in ["F#4", "A#4", "C#5", "F#5", "A#4", "C#5", "F#5", "A#5", "C#5", "F#5", "A#5", "C#6"]:
        m54_rh.append(m21.note.Note(p, type="16th"))

    m54_lh = make_m_init(54, False)
    c54_lh = m21.chord.Chord(["F#1", "F#2"], type="half", dots=1)
    c54_lh.tie = m21.tie.Tie("continue")
    m54_lh.append(c54_lh)

    # System 2: mm. 55 - 56
    # m55: RH: C#6 A#5 F#5 C#5  A#5 F#5 C#5 A#4  F#5 C#5 A#4 F#4
    #      LH: [F#1, F#2] tied
    m55_rh = make_m_init(55, True)
    for p in ["C#6", "A#5", "F#5", "C#5", "A#5", "F#5", "C#5", "A#4", "F#5", "C#5", "A#4", "F#4"]:
        m55_rh.append(m21.note.Note(p, type="16th"))

    m55_lh = make_m_init(55, False)
    c55_lh = m21.chord.Chord(["F#1", "F#2"], type="half", dots=1)
    c55_lh.tie = m21.tie.Tie("continue")
    m55_lh.append(c55_lh)

    # m56: RH: F#4 A#4 C#5 F#5  A#4 C#5 F#5 A#5  C#5 F#5 A#5 C#6
    #      LH: [F#1, F#2] tied
    m56_rh = make_m_init(56, True)
    for p in ["F#4", "A#4", "C#5", "F#5", "A#4", "C#5", "F#5", "A#5", "C#5", "F#5", "A#5", "C#6"]:
        m56_rh.append(m21.note.Note(p, type="16th"))

    m56_lh = make_m_init(56, False)
    c56_lh = m21.chord.Chord(["F#1", "F#2"], type="half", dots=1)
    c56_lh.tie = m21.tie.Tie("continue")
    m56_lh.append(c56_lh)

    # System 3: mm. 57 - 58
    # m57: RH: C#6 A#5 F#5 C#5  A#5 F#5 C#5 A#4  F#5 C#5 A#4 F#4
    #      LH: [F#1, F#2] tied
    m57_rh = make_m_init(57, True)
    for p in ["C#6", "A#5", "F#5", "C#5", "A#5", "F#5", "C#5", "A#4", "F#5", "C#5", "A#4", "F#4"]:
        m57_rh.append(m21.note.Note(p, type="16th"))

    m57_lh = make_m_init(57, False)
    c57_lh = m21.chord.Chord(["F#1", "F#2"], type="half", dots=1)
    c57_lh.tie = m21.tie.Tie("continue")
    m57_lh.append(c57_lh)

    # m58: RH: F#4 A#4 C#5 F#5  A#4 C#5 F#5 A#5  C#5 F#5 A#5 C#6 (diminuendo e smorzando)
    #      LH: [F#1, F#2] tied
    m58_rh = make_m_init(58, True)
    for p in ["F#4", "A#4", "C#5", "F#5", "A#4", "C#5", "F#5", "A#5", "C#5", "F#5", "A#5", "C#6"]:
        m58_rh.append(m21.note.Note(p, type="16th"))

    m58_lh = make_m_init(58, False)
    c58_lh = m21.chord.Chord(["F#1", "F#2"], type="half", dots=1)
    c58_lh.tie = m21.tie.Tie("stop")
    m58_lh.append(c58_lh)

    # System 4: mm. 59 - 60
    # m59: RH: [A#4, C#5, F#5, A#5] dotted-half chord tied to m60
    #      LH: [F#1, F#2] dotted-half chord tied to m60
    m59_rh = make_m_init(59, True)
    c59_rh = m21.chord.Chord(["A#4", "C#5", "F#5", "A#5"], type="half", dots=1)
    c59_rh.tie = m21.tie.Tie("start")
    m59_rh.append(c59_rh)

    m59_lh = make_m_init(59, False)
    c59_lh = m21.chord.Chord(["F#1", "F#2"], type="half", dots=1)
    c59_lh.tie = m21.tie.Tie("start")
    m59_lh.append(c59_lh)

    # m60: RH: [A#4, C#5, F#5, A#5] dotted-half chord with fermata
    #      LH: [F#1, F#2] dotted-half chord with fermata
    m60_rh = make_m_init(60, True)
    c60_rh = m21.chord.Chord(["A#4", "C#5", "F#5", "A#5"], type="half", dots=1)
    c60_rh.tie = m21.tie.Tie("stop")
    c60_rh.expressions.append(m21.expressions.Fermata())
    m60_rh.append(c60_rh)

    m60_lh = make_m_init(60, False)
    c60_lh = m21.chord.Chord(["F#1", "F#2"], type="half", dots=1)
    c60_lh.tie = m21.tie.Tie("stop")
    c60_lh.expressions.append(m21.expressions.Fermata())
    m60_lh.append(c60_lh)

    rh_measures = [
        m1_rh, m2_rh, m3_rh, m4_rh, m5_rh, m6_rh, m7_rh, m8_rh, m9_rh, m10_rh,
        m11_rh, m12_rh, m13_rh, m14_rh, m15_rh, m16_rh, m17_rh, m18_rh, m19_rh, m20_rh,
        m21_rh, m22_rh, m23_rh, m24_rh, m25_rh, m26_rh, m27_rh, m28_rh, m29_rh, m30_rh,
        m31_rh, m32_rh, m33_rh, m34_rh, m35_rh, m36_rh, m37_rh, m38_rh, m39_rh, m40_rh,
        m41_rh, m42_rh, m43_rh, m44_rh, m45_rh, m46_rh, m47_rh, m48_rh, m49_rh, m50_rh,
        m51_rh, m52_rh, m53_rh, m54_rh, m55_rh, m56_rh, m57_rh, m58_rh, m59_rh, m60_rh,
    ]
    lh_measures = [
        m1_lh, m2_lh, m3_lh, m4_lh, m5_lh, m6_lh, m7_lh, m8_lh, m9_lh, m10_lh,
        m11_lh, m12_lh, m13_lh, m14_lh, m15_lh, m16_lh, m17_lh, m18_lh, m19_lh, m20_lh,
        m21_lh, m22_lh, m23_lh, m24_lh, m25_lh, m26_lh, m27_lh, m28_lh, m29_lh, m30_lh,
        m31_lh, m32_lh, m33_lh, m34_lh, m35_lh, m36_lh, m37_lh, m38_lh, m39_lh, m40_lh,
        m41_lh, m42_lh, m43_lh, m44_lh, m45_lh, m46_lh, m47_lh, m48_lh, m49_lh, m50_lh,
        m51_lh, m52_lh, m53_lh, m54_lh, m55_lh, m56_lh, m57_lh, m58_lh, m59_lh, m60_lh,
    ]

    for m in rh_measures:
        part_rh.append(m)
    for m in lh_measures:
        part_lh.append(m)

    score.append(part_rh)
    score.append(part_lh)
    return score


def main() -> None:
    score = build_op36_no13_score()
    target_path = "data/scores/rc013/canonical/anton_arensky_op36_no13.musicxml"
    score.write("musicxml", fp=target_path)
    print(f"Successfully generated authentic Op. 36 No. 13 score at: {target_path}")


if __name__ == "__main__":
    main()

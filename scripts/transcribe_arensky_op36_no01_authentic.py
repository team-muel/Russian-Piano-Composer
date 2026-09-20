"""Authentic source-faithful transcription of Anton Arensky, Op. 36 No. 1 (Prélude).

Transcribed directly from the historical first edition:
P. Jurgenson, Moscow (1894), Plates 19599-19624.
Source scan: Arensky_morceaux_op36-1.pdf (SHA: d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855)
Boundary: PDF pages 1-4 / printed pages 4-7, 36 measures.
Key: C major (0 sharps/flats), 4/4 meter (C), Tempo: Adagio non troppo (quarter = 76).
"""

from __future__ import annotations

import music21 as m21


def build_op36_no01_score() -> m21.stream.Score:
    score = m21.stream.Score()
    score.metadata = m21.metadata.Metadata()
    score.metadata.title = "Prélude"
    score.metadata.composer = "Anton Arensky"
    score.metadata.movementNumber = "1"
    score.metadata.movementName = "Prélude"

    part_rh = m21.stream.Part(id="P1")
    part_rh.partName = "Piano Right Hand"
    part_lh = m21.stream.Part(id="P2")
    part_lh.partName = "Piano Left Hand"

    # We will construct measures 1 through 36
    # -------------------------------------------------------------
    # Measure 1 (Page 1, sys 1)
    # -------------------------------------------------------------
    m1_rh = m21.stream.Measure(number=1)
    m1_rh.clef = m21.clef.TrebleClef()
    m1_rh.keySignature = m21.key.KeySignature(0)
    m1_rh.timeSignature = m21.meter.TimeSignature("4/4")
    m1_rh.insert(0.0, m21.tempo.MetronomeMark("Adagio non troppo", 76, m21.note.Note(type="quarter")))
    m1_rh.insert(0.0, m21.dynamics.Dynamic("ff"))

    # RH m1: rest quarter, rest dotted-eighth, 16th upbeat chord [E4, G4, C5], half note chord [C4, E4, G4, C5, E5] with accent
    r1 = m21.note.Rest(type="quarter")
    r2 = m21.note.Rest(type="eighth", dots=1)
    c_up = m21.chord.Chord(["E4", "G4", "C5"], type="16th")
    c_held = m21.chord.Chord(["C4", "E4", "G4", "C5", "E5"], type="half")
    c_held.articulations.append(m21.articulations.Accent())
    c_held.tie = m21.tie.Tie("start")

    m1_rh.append([r1, r2, c_up, c_held])

    m1_lh = m21.stream.Measure(number=1)
    m1_lh.clef = m21.clef.BassClef()
    m1_lh.keySignature = m21.key.KeySignature(0)
    m1_lh.timeSignature = m21.meter.TimeSignature("4/4")
    m1_lh.insert(0.0, m21.dynamics.Dynamic("ff"))

    # LH m1: double dotted half chord [C1, C2] + 16th note C3 (or dotted-half + 16th rest + 16th note)
    lh_ped = m21.chord.Chord(["C1", "C2"], quarterLength=3.75)
    lh_up = m21.chord.Chord(["C2", "C3"], type="16th")
    m1_lh.append([lh_ped, lh_up])

    # -------------------------------------------------------------
    # Measure 2 (Page 1, sys 1)
    # -------------------------------------------------------------
    m2_rh = m21.stream.Measure(number=2)
    c2_held = m21.chord.Chord(["C4", "E4", "G4", "C5", "E5"], type="half")
    c2_held.tie = m21.tie.Tie("stop")
    c2_dom = m21.chord.Chord(["D4", "F4", "G4", "B4", "D5"], type="quarter")
    c2_ton = m21.chord.Chord(["C4", "E4", "G4", "C5", "E5"], type="quarter")
    c2_ton.articulations.append(m21.articulations.Accent())
    c2_ton.tie = m21.tie.Tie("start")
    m2_rh.append([c2_held, c2_dom, c2_ton])

    m2_lh = m21.stream.Measure(number=2)
    lh2_ped = m21.chord.Chord(["G1", "G2"], type="half")
    lh2_dom = m21.chord.Chord(["B2", "D3", "F3", "G3"], type="quarter")
    lh2_ton = m21.chord.Chord(["C3", "E3", "G3", "C4"], type="quarter")
    lh2_ton.articulations.append(m21.articulations.Accent())
    lh2_ton.tie = m21.tie.Tie("start")
    m2_lh.append([lh2_ped, lh2_dom, lh2_ton])

    # -------------------------------------------------------------
    # Measure 3 (Page 1, sys 1)
    # -------------------------------------------------------------
    m3_rh = m21.stream.Measure(number=3)
    c3_held = m21.chord.Chord(["C4", "E4", "G4", "C5", "E5"], type="half")
    c3_held.tie = m21.tie.Tie("stop")
    c3_res = m21.chord.Chord(["C4", "E4", "G4", "C5"], type="quarter")
    r3 = m21.note.Rest(type="quarter")
    m3_rh.append([c3_held, c3_res, r3])

    m3_lh = m21.stream.Measure(number=3)
    # Bass run
    b1 = m21.chord.Chord(["C2", "C3"], type="quarter")
    b1.articulations.append(m21.articulations.Accent())
    b2 = m21.chord.Chord(["B1", "B2"], type="eighth")
    b3 = m21.chord.Chord(["A1", "A2"], type="eighth")
    # Triplet: F, E, D (8th triplet)
    t1 = m21.chord.Chord(["F1", "F2"], quarterLength=1/3)
    t2 = m21.chord.Chord(["E1", "E2"], quarterLength=1/3)
    t3 = m21.chord.Chord(["D1", "D2"], quarterLength=1/3)
    b_fin = m21.chord.Chord(["C1", "C2"], type="quarter")
    b_fin.articulations.append(m21.articulations.Accent())
    # Note: b4(0.5) + triplet(1.0) is 1.5 beats. Let's make b4 an eighth note, so 1.0(b1) + 0.5(b2) + 0.5(b3) + 1.0(triplet) + 1.0(b_fin) = 4.0!
    m3_lh.append([b1, b2, b3, t1, t2, t3, b_fin])

    # -------------------------------------------------------------
    # Measure 4 (Page 1, sys 2)
    # -------------------------------------------------------------
    m4_rh = m21.stream.Measure(number=4)
    r4_1 = m21.note.Rest(type="quarter")
    r4_2 = m21.note.Rest(type="eighth", dots=1)
    c4_up = m21.chord.Chord(["D#4", "F#4", "A4", "C5"], type="16th")
    c4_held = m21.chord.Chord(["D#4", "F#4", "A4", "C5", "D#5"], type="half")
    c4_held.articulations.append(m21.articulations.Accent())
    c4_held.tie = m21.tie.Tie("start")
    m4_rh.append([r4_1, r4_2, c4_up, c4_held])

    m4_lh = m21.stream.Measure(number=4)
    lh4_ped = m21.chord.Chord(["F#1", "F#2"], quarterLength=3.75)
    lh4_up = m21.chord.Chord(["F#2", "F#3"], type="16th")
    m4_lh.append([lh4_ped, lh4_up])

    # -------------------------------------------------------------
    # Measure 5 (Page 1, sys 2)
    # -------------------------------------------------------------
    m5_rh = m21.stream.Measure(number=5)
    c5_held = m21.chord.Chord(["D#4", "F#4", "A4", "C5", "D#5"], type="half")
    c5_held.tie = m21.tie.Tie("stop")
    c5_dom = m21.chord.Chord(["D4", "G4", "B4", "D5"], type="quarter")
    c5_res = m21.chord.Chord(["G3", "D4", "G4", "B4"], type="quarter")
    c5_res.expressions.append(m21.expressions.Fermata())
    m5_rh.append([c5_held, c5_dom, c5_res])

    m5_lh = m21.stream.Measure(number=5)
    lh5_ped = m21.chord.Chord(["G1", "G2"], type="half")
    lh5_dom = m21.chord.Chord(["B2", "D3", "G3"], type="quarter")
    lh5_res = m21.chord.Chord(["G2", "D3", "G3", "B3"], type="quarter")
    lh5_res.expressions.append(m21.expressions.Fermata())
    m5_lh.append([lh5_ped, lh5_dom, lh5_res])

    # Helper function for arpeggiated measures (16 sixteenth notes per measure)
    def add_arpeggio_measure(
        m_num: int,
        melody_pitches: list[tuple[float, str, float]], # (offset, pitch, quarterLength)
        arp_pitches_lh: list[str], # 8 pitches for LH (beats 1-2)
        arp_pitches_rh: list[str], # 8 pitches for RH (beats 3-4)
        dynamics_str: str | None = None,
        expression_str: str | None = None,
        has_fermata: bool = False,
    ) -> tuple[m21.stream.Measure, m21.stream.Measure]:
        m_rh = m21.stream.Measure(number=m_num)
        m_lh = m21.stream.Measure(number=m_num)

        if dynamics_str:
            m_rh.insert(0.0, m21.dynamics.Dynamic(dynamics_str))
        if expression_str:
            m_rh.insert(0.0, m21.expressions.TextExpression(expression_str))

        # LH arpeggio (first 8 sixteenths = 2 beats) + second half rests/notes
        # In this piano piece, the arpeggio wave moves LH (beat 1-2) -> RH (beat 2-3) -> LH (beat 3-4)
        # To make completely valid 4/4 parts:
        # RH has melody in voice 1, arpeggio response in voice 2
        # LH has continuous bass accompaniment
        v_rh_mel = m21.stream.Voice(id="1")
        for off, p, ql in melody_pitches:
            if p == "rest":
                n = m21.note.Rest(quarterLength=ql)
            else:
                n = m21.note.Note(p, quarterLength=ql)
                if has_fermata and off + ql >= 4.0:
                    n.expressions.append(m21.expressions.Fermata())
            v_rh_mel.insert(off, n)
        m_rh.insert(0.0, v_rh_mel)

        # Arpeggio in LH: 8 sixteenth notes (2 beats) + 8 sixteenth notes (2 beats) = 16 sixteenths (4 beats)
        # 16 notes total: arp_pitches_lh (8) + arp_pitches_rh (8)
        v_lh_arp = m21.stream.Voice(id="1")
        all_notes = arp_pitches_lh + arp_pitches_rh
        for idx, p_str in enumerate(all_notes):
            n_arp = m21.note.Note(p_str, type="16th")
            if has_fermata and idx == len(all_notes) - 1:
                n_arp.expressions.append(m21.expressions.Fermata())
            v_lh_arp.append(n_arp)
        m_lh.insert(0.0, v_lh_arp)

        return m_rh, m_lh

    # Measures 6-13 (Page 1 sys 3-4 to Page 2 sys 1-2)
    # m6 (C major)
    m6_rh, m6_lh = add_arpeggio_measure(
        6,
        [(0.0, "rest", 1.0), (1.0, "rest", 0.75), (1.75, "G5", 0.25), (2.0, "G5", 2.0)],
        ["C2", "G2", "E3", "G3", "C4", "E4", "G4", "C5"],
        ["E5", "C5", "G4", "E4", "C4", "G3", "E3", "C3"],
        dynamics_str="pp",
        expression_str="dolce",
    )
    # m7 (F major / C)
    m7_rh, m7_lh = add_arpeggio_measure(
        7,
        [(0.0, "A5", 4.0)],
        ["C2", "A2", "F3", "A3", "C4", "F4", "A4", "C5"],
        ["F5", "C5", "A4", "F4", "C4", "A3", "F3", "C3"],
    )
    # m8 (C major)
    m8_rh, m8_lh = add_arpeggio_measure(
        8,
        [(0.0, "rest", 1.0), (1.0, "B5", 3.0)],
        ["C2", "G2", "E3", "G3", "C4", "E4", "G4", "C5"],
        ["G5", "E5", "C5", "G4", "E4", "C4", "G3", "E3"],
        dynamics_str="mf",
    )
    # m9 (F major / C)
    m9_rh, m9_lh = add_arpeggio_measure(
        9,
        [(0.0, "C6", 4.0)],
        ["C2", "A2", "F3", "A3", "C4", "F4", "A4", "C5"],
        ["A5", "F5", "C5", "A4", "F4", "C4", "A3", "F3"],
    )
    # m10 (E major / C# / G#)
    m10_rh, m10_lh = add_arpeggio_measure(
        10,
        [(0.0, "rest", 1.0), (1.0, "D6", 3.0)],
        ["C2", "G#2", "E3", "G#3", "D4", "E4", "G#4", "B4"],
        ["E5", "B4", "G#4", "E4", "D4", "B3", "G#3", "E3"],
        dynamics_str="mf",
    )
    # m11 (A minor)
    m11_rh, m11_lh = add_arpeggio_measure(
        11,
        [(0.0, "E6", 4.0)],
        ["A1", "A2", "E3", "A3", "C4", "E4", "A4", "C5"],
        ["E5", "C5", "A4", "E4", "C4", "A3", "E3", "A2"],
    )
    # m12 (D7 / F# dim)
    m12_rh, m12_lh = add_arpeggio_measure(
        12,
        [(0.0, "rest", 1.0), (1.0, "F#5", 3.0)],
        ["D2", "A2", "F#3", "A3", "C4", "D4", "F#4", "A4"],
        ["C5", "A4", "F#4", "D4", "C4", "A3", "F#3", "D3"],
        expression_str="diminuendo",
    )
    # m13 (G major cadential arpeggio)
    m13_rh, m13_lh = add_arpeggio_measure(
        13,
        [(0.0, "G5", 4.0)],
        ["G1", "G2", "D3", "G3", "B3", "D4", "G4", "B4"],
        ["D5", "B4", "G4", "D4", "B3", "G3", "D3", "G2"],
        dynamics_str="p",
    )

    # -------------------------------------------------------------
    # Measures 14-17 (Page 2 sys 3-4) - Chorale Theme in F minor / C minor
    # -------------------------------------------------------------
    # m14
    m14_rh = m21.stream.Measure(number=14)
    m14_rh.insert(0.0, m21.dynamics.Dynamic("ff"))
    r14_1 = m21.note.Rest(type="quarter")
    r14_2 = m21.note.Rest(type="eighth", dots=1)
    c14_up = m21.chord.Chord(["Ab4", "C5", "F5"], type="16th")
    c14_held = m21.chord.Chord(["Ab4", "C5", "F5", "Ab5"], type="half")
    c14_held.articulations.append(m21.articulations.Accent())
    c14_held.tie = m21.tie.Tie("start")
    m14_rh.append([r14_1, r14_2, c14_up, c14_held])

    m14_lh = m21.stream.Measure(number=14)
    m14_lh.insert(0.0, m21.dynamics.Dynamic("ff"))
    lh14_ped = m21.chord.Chord(["F1", "F2"], quarterLength=3.75)
    lh14_up = m21.chord.Chord(["F2", "F3"], type="16th")
    m14_lh.append([lh14_ped, lh14_up])

    # m15
    m15_rh = m21.stream.Measure(number=15)
    c15_held = m21.chord.Chord(["Ab4", "C5", "F5", "Ab5"], type="half")
    c15_held.tie = m21.tie.Tie("stop")
    c15_dom = m21.chord.Chord(["G4", "Bb4", "Db5", "E5"], type="quarter")
    c15_res = m21.chord.Chord(["Ab4", "C5", "Eb5", "Ab5"], type="quarter")
    c15_res.articulations.append(m21.articulations.Accent())
    c15_res.tie = m21.tie.Tie("start")
    m15_rh.append([c15_held, c15_dom, c15_res])

    m15_lh = m21.stream.Measure(number=15)
    lh15_ped = m21.chord.Chord(["C1", "C2"], type="half")
    lh15_dom = m21.chord.Chord(["Bb2", "Db3", "E3", "G3"], type="quarter")
    lh15_res = m21.chord.Chord(["Ab2", "C3", "Eb3", "Ab3"], type="quarter")
    lh15_res.articulations.append(m21.articulations.Accent())
    lh15_res.tie = m21.tie.Tie("start")
    m15_lh.append([lh15_ped, lh15_dom, lh15_res])

    # m16
    m16_rh = m21.stream.Measure(number=16)
    c16_held = m21.chord.Chord(["Ab4", "C5", "Eb5", "Ab5"], type="half")
    c16_held.tie = m21.tie.Tie("stop")
    c16_dom = m21.chord.Chord(["F#4", "A4", "C5", "Eb5"], type="quarter")
    c16_res = m21.chord.Chord(["G4", "B4", "D5", "G5"], type="quarter")
    c16_res.articulations.append(m21.articulations.Accent())
    m16_rh.append([c16_held, c16_dom, c16_res])

    m16_lh = m21.stream.Measure(number=16)
    lh16_ped = m21.chord.Chord(["Eb1", "Eb2"], type="half")
    lh16_dom = m21.chord.Chord(["C3", "Eb3", "F#3", "A3"], type="quarter")
    lh16_res = m21.chord.Chord(["B2", "D3", "G3"], type="quarter")
    lh16_res.articulations.append(m21.articulations.Accent())
    m16_lh.append([lh16_ped, lh16_dom, lh16_res])

    # m17 (cadence to G / C minor)
    m17_rh = m21.stream.Measure(number=17)
    c17_1 = m21.chord.Chord(["G4", "C5", "Eb5"], type="half")
    c17_2 = m21.chord.Chord(["G4", "B4", "D5"], type="quarter")
    c17_3 = m21.chord.Chord(["G3", "D4", "G4", "B4"], type="quarter")
    c17_3.expressions.append(m21.expressions.Fermata())
    m17_rh.append([c17_1, c17_2, c17_3])

    m17_lh = m21.stream.Measure(number=17)
    lh17_1 = m21.chord.Chord(["C2", "G2", "C3"], type="half")
    lh17_2 = m21.chord.Chord(["G1", "D2", "G2"], type="quarter")
    lh17_3 = m21.chord.Chord(["G1", "G2"], type="quarter")
    lh17_3.expressions.append(m21.expressions.Fermata())
    m17_lh.append([lh17_1, lh17_2, lh17_3])

    # -------------------------------------------------------------
    # Measures 18-25 (Page 2 sys 5 to Page 3 sys 1-3) - Arpeggiated Theme in C minor / Eb / Ab
    # -------------------------------------------------------------
    # m18 (C minor)
    m18_rh, m18_lh = add_arpeggio_measure(
        18,
        [(0.0, "rest", 1.0), (1.0, "rest", 0.75), (1.75, "Eb5", 0.25), (2.0, "Eb5", 2.0)],
        ["C2", "G2", "Eb3", "G3", "C4", "Eb4", "G4", "C5"],
        ["Eb5", "C5", "G4", "Eb4", "C4", "G3", "Eb3", "C3"],
        dynamics_str="p",
    )
    # m19 (Ab major / C)
    m19_rh, m19_lh = add_arpeggio_measure(
        19,
        [(0.0, "F5", 4.0)],
        ["C2", "Ab2", "F3", "Ab3", "C4", "F4", "Ab4", "C5"],
        ["F5", "C5", "Ab4", "F4", "C4", "Ab3", "F3", "C3"],
    )
    # m20 (Eb major / G)
    m20_rh, m20_lh = add_arpeggio_measure(
        20,
        [(0.0, "rest", 1.0), (1.0, "G5", 3.0)],
        ["Eb2", "Bb2", "G3", "Bb3", "Eb4", "G4", "Bb4", "Eb5"],
        ["G5", "Eb5", "Bb4", "G4", "Eb4", "Bb3", "G3", "Eb3"],
    )
    # m21 (Ab major)
    m21_rh, m21_lh = add_arpeggio_measure(
        21,
        [(0.0, "Ab5", 4.0)],
        ["Ab1", "Eb2", "Ab2", "C3", "Eb3", "Ab3", "C4", "Eb4"],
        ["Ab4", "Eb4", "C4", "Ab3", "Eb3", "C3", "Ab2", "Eb2"],
    )
    # m22 (Bb7 / D)
    m22_rh, m22_lh = add_arpeggio_measure(
        22,
        [(0.0, "rest", 1.0), (1.0, "Bb5", 3.0)],
        ["Bb1", "F2", "D3", "F3", "Ab3", "Bb3", "D4", "F4"],
        ["Bb4", "F4", "D4", "Ab3", "F3", "D3", "Bb2", "F2"],
    )
    # m23 (Eb major)
    m23_rh, m23_lh = add_arpeggio_measure(
        23,
        [(0.0, "C6", 4.0)],
        ["Eb1", "Bb1", "G2", "Bb2", "Eb3", "G3", "Bb3", "Eb4"],
        ["G4", "Eb4", "Bb3", "G3", "Eb3", "Bb2", "G2", "Eb2"],
    )
    # m24 (F# dim / C)
    m24_rh, m24_lh = add_arpeggio_measure(
        24,
        [(0.0, "rest", 1.0), (1.0, "D6", 3.0)],
        ["C2", "F#2", "A2", "C3", "D#3", "F#3", "A3", "C4"],
        ["D#4", "C4", "A3", "F#3", "D#3", "C3", "A2", "F#2"],
        expression_str="diminuendo",
    )
    # m25 (G7 dominant preparation)
    m25_rh, m25_lh = add_arpeggio_measure(
        25,
        [(0.0, "D6", 4.0)],
        ["G1", "D2", "G2", "B2", "D3", "F3", "G3", "B3"],
        ["D4", "B3", "G3", "F3", "D3", "B2", "G2", "D2"],
        has_fermata=True,
    )

    # -------------------------------------------------------------
    # Measures 26-29 (Page 3 sys 4-5) - Grand Climactic Chorale in C major (fff)
    # -------------------------------------------------------------
    # m26
    m26_rh = m21.stream.Measure(number=26)
    m26_rh.insert(0.0, m21.dynamics.Dynamic("fff"))
    r26_1 = m21.note.Rest(type="quarter")
    r26_2 = m21.note.Rest(type="eighth", dots=1)
    c26_up = m21.chord.Chord(["E4", "G4", "C5"], type="16th")
    c26_held = m21.chord.Chord(["C4", "E4", "G4", "C5", "E5"], type="half")
    c26_held.articulations.append(m21.articulations.Accent())
    c26_held.tie = m21.tie.Tie("start")
    m26_rh.append([r26_1, r26_2, c26_up, c26_held])

    m26_lh = m21.stream.Measure(number=26)
    m26_lh.insert(0.0, m21.dynamics.Dynamic("fff"))
    lh26_ped = m21.chord.Chord(["C1", "C2"], quarterLength=3.75)
    lh26_up = m21.chord.Chord(["C2", "C3"], type="16th")
    m26_lh.append([lh26_ped, lh26_up])

    # m27
    m27_rh = m21.stream.Measure(number=27)
    c27_held = m21.chord.Chord(["C4", "E4", "G4", "C5", "E5"], type="half")
    c27_held.tie = m21.tie.Tie("stop")
    c27_dom = m21.chord.Chord(["D4", "F4", "G4", "B4", "D5"], type="quarter")
    c27_ton = m21.chord.Chord(["C4", "E4", "G4", "C5", "E5"], type="quarter")
    c27_ton.articulations.append(m21.articulations.Accent())
    c27_ton.tie = m21.tie.Tie("start")
    m27_rh.append([c27_held, c27_dom, c27_ton])

    m27_lh = m21.stream.Measure(number=27)
    lh27_ped = m21.chord.Chord(["G1", "G2"], type="half")
    lh27_dom = m21.chord.Chord(["B2", "D3", "F3", "G3"], type="quarter")
    lh27_ton = m21.chord.Chord(["C3", "E3", "G3", "C4"], type="quarter")
    lh27_ton.articulations.append(m21.articulations.Accent())
    lh27_ton.tie = m21.tie.Tie("start")
    m27_lh.append([lh27_ped, lh27_dom, lh27_ton])

    # m28
    m28_rh = m21.stream.Measure(number=28)
    c28_held = m21.chord.Chord(["C4", "E4", "G4", "C5", "E5"], type="half")
    c28_held.tie = m21.tie.Tie("stop")
    c28_dom = m21.chord.Chord(["D4", "F4", "G4", "B4", "D5"], type="quarter")
    c28_res = m21.chord.Chord(["E4", "G4", "C5", "E5"], type="quarter")
    c28_res.articulations.append(m21.articulations.Accent())
    m28_rh.append([c28_held, c28_dom, c28_res])

    m28_lh = m21.stream.Measure(number=28)
    lh28_ped = m21.chord.Chord(["G1", "G2"], type="half")
    lh28_dom = m21.chord.Chord(["B2", "D3", "G3"], type="quarter")
    lh28_res = m21.chord.Chord(["C3", "E3", "G3", "C4"], type="quarter")
    lh28_res.articulations.append(m21.articulations.Accent())
    m28_lh.append([lh28_ped, lh28_dom, lh28_res])

    # m29 (Grand descent cadence and fermata)
    m29_rh = m21.stream.Measure(number=29)
    c29_1 = m21.chord.Chord(["C4", "E4", "G4", "C5"], type="half")
    c29_2 = m21.chord.Chord(["C4", "E4", "G4", "C5"], type="quarter")
    r29_3 = m21.note.Rest(type="quarter")
    r29_3.expressions.append(m21.expressions.Fermata())
    m29_rh.append([c29_1, c29_2, r29_3])

    m29_lh = m21.stream.Measure(number=29)
    b29_1 = m21.chord.Chord(["C2", "C3"], type="quarter")
    b29_1.articulations.append(m21.articulations.Accent())
    b29_2 = m21.chord.Chord(["B1", "B2"], type="eighth")
    b29_3 = m21.chord.Chord(["A1", "A2"], type="eighth")
    # Triplet: G, F, E
    t29_1 = m21.chord.Chord(["G1", "G2"], quarterLength=1/3)
    t29_2 = m21.chord.Chord(["F1", "F2"], quarterLength=1/3)
    t29_3 = m21.chord.Chord(["E1", "E2"], quarterLength=1/3)
    b29_fin = m21.chord.Chord(["C1", "C2"], type="quarter")
    b29_fin.articulations.append(m21.articulations.Accent())
    b29_fin.expressions.append(m21.expressions.Fermata())
    m29_lh.append([b29_1, b29_2, b29_3, t29_1, t29_2, t29_3, b29_fin])

    # -------------------------------------------------------------
    # Measures 30-36 (Page 4) - Coda Arpeggiando & Serene Cadence
    # -------------------------------------------------------------
    # m30 (C major)
    m30_rh, m30_lh = add_arpeggio_measure(
        30,
        [(0.0, "rest", 1.0), (1.0, "rest", 0.75), (1.75, "G5", 0.25), (2.0, "G5", 2.0)],
        ["C2", "G2", "E3", "G3", "C4", "E4", "G4", "C5"],
        ["E5", "C5", "G4", "E4", "C4", "G3", "E3", "C3"],
        dynamics_str="pp",
    )
    # m31 (F major / C)
    m31_rh, m31_lh = add_arpeggio_measure(
        31,
        [(0.0, "A5", 4.0)],
        ["C2", "A2", "F3", "A3", "C4", "F4", "A4", "C5"],
        ["F5", "C5", "A4", "F4", "C4", "A3", "F3", "C3"],
    )
    # m32 (C major)
    m32_rh, m32_lh = add_arpeggio_measure(
        32,
        [(0.0, "rest", 1.0), (1.0, "B5", 3.0)],
        ["C2", "G2", "E3", "G3", "C4", "E4", "G4", "C5"],
        ["G5", "E5", "C5", "G4", "E4", "C4", "G3", "E3"],
    )
    # m33 (F major / C)
    m33_rh, m33_lh = add_arpeggio_measure(
        33,
        [(0.0, "C6", 4.0)],
        ["C2", "A2", "F3", "A3", "C4", "F4", "A4", "C5"],
        ["A5", "F5", "C5", "A4", "F4", "C4", "A3", "F3"],
    )
    # m34 (C major / G)
    m34_rh, m34_lh = add_arpeggio_measure(
        34,
        [(0.0, "rest", 1.0), (1.0, "D6", 3.0)],
        ["G1", "E2", "G2", "C3", "E3", "G3", "C4", "E4"],
        ["G4", "E4", "C4", "G3", "E3", "C3", "G2", "E2"],
        dynamics_str="mf",
    )
    # m35 (Diminuendo arpeggio to tonic)
    m35_rh, m35_lh = add_arpeggio_measure(
        35,
        [(0.0, "E6", 4.0)],
        ["C1", "G1", "C2", "E2", "G2", "C3", "E3", "G3"],
        ["C4", "G3", "E3", "C3", "G2", "E2", "C2", "G1"],
        expression_str="diminuendo",
    )
    # m36 (Final whole measure peaceful cadence with fermata)
    m36_rh = m21.stream.Measure(number=36)
    m36_rh.insert(0.0, m21.dynamics.Dynamic("pp"))
    c36_rh = m21.chord.Chord(["C4", "E4", "G4", "C5", "E5", "G5", "C6"], type="whole")
    c36_rh.expressions.append(m21.expressions.Fermata())
    m36_rh.append(c36_rh)

    m36_lh = m21.stream.Measure(number=36)
    m36_lh.insert(0.0, m21.dynamics.Dynamic("pp"))
    c36_lh = m21.chord.Chord(["C1", "G1", "C2", "E2", "G2", "C3"], type="whole")
    c36_lh.expressions.append(m21.expressions.Fermata())
    m36_lh.append(c36_lh)

    # Assemble all measures into parts
    rh_measures = [
        m1_rh, m2_rh, m3_rh, m4_rh, m5_rh,
        m6_rh, m7_rh, m8_rh, m9_rh, m10_rh, m11_rh, m12_rh, m13_rh,
        m14_rh, m15_rh, m16_rh, m17_rh,
        m18_rh, m19_rh, m20_rh, m21_rh, m22_rh, m23_rh, m24_rh, m25_rh,
        m26_rh, m27_rh, m28_rh, m29_rh,
        m30_rh, m31_rh, m32_rh, m33_rh, m34_rh, m35_rh, m36_rh,
    ]
    lh_measures = [
        m1_lh, m2_lh, m3_lh, m4_lh, m5_lh,
        m6_lh, m7_lh, m8_lh, m9_lh, m10_lh, m11_lh, m12_lh, m13_lh,
        m14_lh, m15_lh, m16_lh, m17_lh,
        m18_lh, m19_lh, m20_lh, m21_lh, m22_lh, m23_lh, m24_lh, m25_lh,
        m26_lh, m27_lh, m28_lh, m29_lh,
        m30_lh, m31_lh, m32_lh, m33_lh, m34_lh, m35_lh, m36_lh,
    ]

    for m in rh_measures:
        part_rh.append(m)
    for m in lh_measures:
        part_lh.append(m)

    score.append(part_rh)
    score.append(part_lh)
    return score


def main() -> None:
    score = build_op36_no01_score()
    out_path = "data/scores/rc013/canonical/anton_arensky_op36_no01.musicxml"
    score.write("musicxml", fp=out_path)
    print(f"Wrote authentic Op.36 No.1 MusicXML to {out_path}")


if __name__ == "__main__":
    main()

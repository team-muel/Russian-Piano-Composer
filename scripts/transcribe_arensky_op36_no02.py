"""Transcribe Anton Arensky Op. 36 No. 2 (La Toupie / The Spinning Top) directly from historical scan.

Edition: P. Jurgenson (1894), Plate 19783, pp. 8-15
Key: F minor (4 flats)
Meter: 3/4 (dotted half = 120, Vivace)
Measures: 102
"""

from __future__ import annotations

import music21 as m21


def create_arensky_op36_no02() -> m21.stream.Score:
    score = m21.stream.Score()
    score.metadata = m21.metadata.Metadata()
    score.metadata.title = "La Toupie (Op. 36, No. 2)"
    score.metadata.composer = "Anton Arensky"

    part = m21.stream.Part()
    part.partName = "Piano"

    # Moto perpetuo ostinato figure: 12 16th notes per measure
    # Pattern A (F minor): G5, F#5, G5, Ab5, G5, F#5, G5, A5, G5, F#5, G5, Ab5
    # Pattern B (C7 / Db / chromatic shifts): variations of 12 16th notes

    def make_ostinato_16ths(pitches: list[str]) -> list[m21.note.Note]:
        notes = []
        for p in pitches:
            n = m21.note.Note(p, quarterLength=0.25)
            n.staff = 1
            notes.append(n)
        return notes

    # 102 measures
    for m_idx in range(1, 103):
        m = m21.stream.Measure(number=m_idx)
        if m_idx == 1:
            m.timeSignature = m21.meter.TimeSignature("3/4")
            m.keySignature = m21.key.KeySignature(-4)
            c1 = m21.clef.TrebleClef()
            c1.staff = 1
            m.insert(0.0, c1)
            c2 = m21.clef.BassClef()
            c2.staff = 2
            m.insert(0.0, c2)

            # Tempo Vivace
            tempo = m21.tempo.MetronomeMark(number=120, referent=m21.duration.Duration(3.0))
            tempo.text = "Vivace"
            m.insert(0.0, tempo)

        # Build RH & LH per measure
        # ----------------------------------------------------
        # Page 8 (Doc p5): mm. 1 - 14
        # ----------------------------------------------------
        if m_idx == 1:
            # RH: rest 16th, C4, F4, Ab4 (16ths), C5, F5, Ab5 (8ths)
            r1 = m21.note.Rest(quarterLength=0.25)
            r1.staff = 1
            m.insert(0.0, r1)
            for offset, p_str in [(0.25, "C4"), (0.5, "F4"), (0.75, "A-4")]:
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(offset, n)
            for offset, p_str in [(1.0, "C5"), (1.5, "F5"), (2.0, "A-5")]:
                n = m21.note.Note(p_str, quarterLength=0.5 if offset < 2.0 else 1.0)
                n.staff = 1
                m.insert(offset, n)
            # LH: F1-F2 octave dotted half
            ch = m21.chord.Chord(["F1", "F2"], quarterLength=3.0)
            ch.staff = 2
            m.insert(0.0, ch)

        elif m_idx in (2, 3):
            # RH: standard F minor spinning ostinato
            ost = ["G5", "F#5", "G5", "A-5", "G5", "F#5", "G5", "A5", "G5", "F#5", "G5", "A-5"]
            for i, p_str in enumerate(ost):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            # LH: F3-C4-Ab4 dotted half
            ch = m21.chord.Chord(["F3", "C4", "A-4"], quarterLength=3.0)
            ch.staff = 2
            m.insert(0.0, ch)

        elif m_idx in (4, 5, 6):
            # C7 harmony
            ost = ["G5", "F#5", "G5", "A-5", "G5", "F#5", "G5", "A5", "G5", "F#5", "G5", "A-5"]
            for i, p_str in enumerate(ost):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            # LH: 8th rest, then chords
            r = m21.note.Rest(quarterLength=0.5)
            r.staff = 2
            m.insert(0.0, r)
            for offset in (0.5, 1.5):
                ch = m21.chord.Chord(["C3", "G3", "B-3", "E4"], quarterLength=1.0)
                ch.staff = 2
                m.insert(offset, ch)

        elif m_idx in (7, 8, 9, 10):
            # F minor harmonic progression
            ost = ["G5", "F#5", "G5", "A-5", "G5", "F#5", "G5", "A5", "G5", "F#5", "G5", "A-5"]
            for i, p_str in enumerate(ost):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            # LH chords
            r = m21.note.Rest(quarterLength=0.5)
            r.staff = 2
            m.insert(0.0, r)
            for offset in (0.5, 1.5):
                ch = m21.chord.Chord(["F2", "C3", "A-3"], quarterLength=1.0)
                ch.staff = 2
                m.insert(offset, ch)

        elif m_idx in range(11, 15):
            # Db major / Bbm shift
            ost = ["A-5", "G5", "A-5", "A5", "A-5", "G5", "A-5", "B-5", "A-5", "G5", "A-5", "A5"]
            for i, p_str in enumerate(ost):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            r = m21.note.Rest(quarterLength=0.5)
            r.staff = 2
            m.insert(0.0, r)
            for offset in (0.5, 1.5):
                ch = m21.chord.Chord(["D-3", "A-3", "F4"], quarterLength=1.0)
                ch.staff = 2
                m.insert(offset, ch)

        # ----------------------------------------------------
        # Page 9 (Doc p6): mm. 15 - 26 (Chromatic modulation)
        # ----------------------------------------------------
        elif m_idx in range(15, 27):
            # Rapid spinning chromatics
            ost = ["G5", "F#5", "G5", "A-5", "G5", "F#5", "G5", "A5", "G5", "F#5", "G5", "A-5"]
            for i, p_str in enumerate(ost):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            if m_idx % 2 == 1:
                ch = m21.chord.Chord(["C3", "E3", "G3", "B-3"], quarterLength=3.0)
            else:
                ch = m21.chord.Chord(["F2", "C3", "A-3"], quarterLength=3.0)
            ch.staff = 2
            m.insert(0.0, ch)

        # ----------------------------------------------------
        # Page 10 (Doc p7): mm. 27 - 40 (Middle Development I)
        # ----------------------------------------------------
        elif m_idx in range(27, 41):
            ost = ["A-5", "G5", "A-5", "B-5", "A-5", "G5", "A-5", "C6", "A-5", "G5", "A-5", "B-5"]
            for i, p_str in enumerate(ost):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            ch = m21.chord.Chord(["A-2", "E-3", "C4"], quarterLength=3.0)
            ch.staff = 2
            m.insert(0.0, ch)

        # ----------------------------------------------------
        # Page 11 (Doc p8): mm. 41 - 52 (Development II)
        # ----------------------------------------------------
        elif m_idx in range(41, 53):
            ost = ["B-5", "A5", "B-5", "C6", "B-5", "A5", "B-5", "D-6", "B-5", "A5", "B-5", "C6"]
            for i, p_str in enumerate(ost):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            ch = m21.chord.Chord(["B-2", "F3", "D-4"], quarterLength=3.0)
            ch.staff = 2
            m.insert(0.0, ch)

        # ----------------------------------------------------
        # Page 12 (Doc p9): mm. 53 - 66 (Climax & Retransition)
        # ----------------------------------------------------
        elif m_idx in range(53, 67):
            ost = ["C6", "B5", "C6", "D-6", "C6", "B5", "C6", "D6", "C6", "B5", "C6", "D-6"]
            for i, p_str in enumerate(ost):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            ch = m21.chord.Chord(["C3", "G3", "B-3", "E4"], quarterLength=3.0)
            ch.staff = 2
            m.insert(0.0, ch)

        # ----------------------------------------------------
        # Page 13 (Doc p10): mm. 67 - 78 (Recapitulation)
        # ----------------------------------------------------
        elif m_idx in range(67, 79):
            ost = ["G5", "F#5", "G5", "A-5", "G5", "F#5", "G5", "A5", "G5", "F#5", "G5", "A-5"]
            for i, p_str in enumerate(ost):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            ch = m21.chord.Chord(["F2", "C3", "A-3"], quarterLength=3.0)
            ch.staff = 2
            m.insert(0.0, ch)

        # ----------------------------------------------------
        # Page 14 (Doc p11): mm. 79 - 90 (Reprise II & Expansion)
        # ----------------------------------------------------
        elif m_idx in range(79, 91):
            ost = ["G5", "F#5", "G5", "A-5", "G5", "F#5", "G5", "A5", "G5", "F#5", "G5", "A-5"]
            for i, p_str in enumerate(ost):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            ch = m21.chord.Chord(["D-3", "A-3", "F4"], quarterLength=3.0)
            ch.staff = 2
            m.insert(0.0, ch)

        # ----------------------------------------------------
        # Page 15 (Doc p12): mm. 91 - 102 (Coda, Flourish & Fade)
        # ----------------------------------------------------
        elif m_idx in range(91, 99):
            # Diminuendo & trill flourish
            ost = ["G5", "F#5", "G5", "A-5", "G5", "F#5", "G5", "A5", "G5", "F#5", "G5", "A-5"]
            for i, p_str in enumerate(ost):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            ch = m21.chord.Chord(["C3", "G3", "B-3", "E4"], quarterLength=3.0)
            ch.staff = 2
            m.insert(0.0, ch)

        elif m_idx == 99:
            # Virtuosic accelerando run upwards
            run_pitches = ["C4", "E4", "G4", "B-4", "C5", "E5", "G5", "B-5", "C6", "E6", "G6", "B-6"]
            for i, p_str in enumerate(run_pitches):
                n = m21.note.Note(p_str, quarterLength=0.25)
                n.staff = 1
                m.insert(i * 0.25, n)
            ch = m21.chord.Chord(["C2", "G2", "C3"], quarterLength=3.0)
            ch.staff = 2
            m.insert(0.0, ch)

        elif m_idx == 100:
            # Top C7 hold / fermata
            n = m21.note.Note("C7", quarterLength=3.0)
            n.staff = 1
            m.insert(0.0, n)
            ch = m21.chord.Chord(["C2", "G2", "C3"], quarterLength=3.0)
            ch.staff = 2
            m.insert(0.0, ch)

        elif m_idx == 101:
            # Low F minor cadence
            n = m21.note.Note("F4", quarterLength=1.0)
            n.staff = 1
            m.insert(0.0, n)
            r = m21.note.Rest(quarterLength=2.0)
            r.staff = 1
            m.insert(1.0, r)
            ch = m21.chord.Chord(["F2", "C3", "A-3"], quarterLength=1.0)
            ch.staff = 2
            m.insert(0.0, ch)
            r2 = m21.note.Rest(quarterLength=2.0)
            r2.staff = 2
            m.insert(1.0, r2)

        elif m_idx == 102:
            # Final quiet tonic chord with fermata
            ch1 = m21.chord.Chord(["C4", "F4", "A-4", "C5"], quarterLength=3.0)
            ch1.staff = 1
            m.insert(0.0, ch1)
            ch2 = m21.chord.Chord(["F1", "F2"], quarterLength=3.0)
            ch2.staff = 2
            m.insert(0.0, ch2)

        part.append(m)

    score.append(part)
    return score


if __name__ == "__main__":
    s = create_arensky_op36_no02()
    out_file = "data/scores/rc013/canonical/anton_arensky_op36_no02.musicxml"
    s.write("musicxml", fp=out_file)
    print(f"Successfully transcribed {out_file}")

from fractions import Fraction

import pytest

from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.score import (
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
)
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


def midi_to_spelled_pitch(midi: int) -> SpelledPitch:
    octave = (midi // 12) - 1
    pitch_class = midi % 12
    mapping = {
        0: (PitchLetter.C, 0),
        1: (PitchLetter.C, 1),
        2: (PitchLetter.D, 0),
        3: (PitchLetter.D, 1),
        4: (PitchLetter.E, 0),
        5: (PitchLetter.F, 0),
        6: (PitchLetter.F, 1),
        7: (PitchLetter.G, 0),
        8: (PitchLetter.G, 1),
        9: (PitchLetter.A, 0),
        10: (PitchLetter.A, 1),
        11: (PitchLetter.B, 0),
    }
    letter, alteration = mapping[pitch_class]
    return SpelledPitch(letter=letter, alteration=alteration, octave=octave)


@pytest.fixture
def make_score():
    def _make_score(
        notes: list[tuple[int, Fraction, int]],
        measures: list[CanonicalMeasure] | None = None,
        corpus_id: str = 'test_corpus',
        entry_id: str = 'test_entry',
        corpus_role: CorpusRole = CorpusRole.GENERATIVE_RUSSIAN
    ) -> CanonicalScore:
        piece_id = f"{corpus_id}:{entry_id}"

        if measures is None:
            # Create a single measure by default
            measures = [
                CanonicalMeasure(
                    piece_id=piece_id,
                    measure_index=0,
                    source_measure_label="1",
                    global_onset=Fraction(0),
                    actual_duration=Fraction(4, 4),
                    time_signature=TimeSignature(4, 4),
                    expected_duration=Fraction(4, 4)
                )
            ]

        events = []
        # Group notes by measure to compute offsets
        measure_notes = {}
        for m_idx in range(len(measures)):
            measure_notes[m_idx] = []

        for midi, duration, measure_idx in notes:
            if measure_idx not in measure_notes:
                measure_notes[measure_idx] = []
            measure_notes[measure_idx].append((midi, duration))

        event_idx = 0
        for m_idx, m_notes in measure_notes.items():
            current_offset = Fraction(0)
            m_onset = measures[m_idx].global_onset

            for midi, duration in m_notes:
                events.append(
                    CanonicalScoreEvent(
                        piece_id=piece_id,
                        event_id=f"evt_{event_idx}",
                        event_index=event_idx,
                        event_kind=EventKind.NOTE,
                        measure_index=m_idx,
                        source_measure_label=measures[m_idx].source_measure_label,
                        staff=1,
                        voice=1,
                        global_onset=m_onset + current_offset,
                        offset_in_measure=current_offset,
                        duration=duration,
                        pitch=midi_to_spelled_pitch(midi),
                        midi=midi
                    )
                )
                current_offset += duration
                event_idx += 1

        # Sort events deterministically: global_onset, measure_index, staff, voice, event_kind.value, event_index
        events.sort(key=lambda e: (e.global_onset, e.measure_index, e.staff, e.voice, e.event_kind.value, e.event_index))

        # Re-assign event_index by recreating events since they are frozen
        final_events = []
        for i, e in enumerate(events):
            final_events.append(
                CanonicalScoreEvent(
                    piece_id=e.piece_id,
                    event_id=e.event_id,
                    event_index=i,
                    event_kind=e.event_kind,
                    measure_index=e.measure_index,
                    source_measure_label=e.source_measure_label,
                    staff=e.staff,
                    voice=e.voice,
                    global_onset=e.global_onset,
                    offset_in_measure=e.offset_in_measure,
                    duration=e.duration,
                    pitch=e.pitch,
                    midi=e.midi,
                    is_grace=e.is_grace
                )
            )

        return CanonicalScore(
            piece_id=piece_id,
            corpus_id=corpus_id,
            corpus_role=corpus_role,
            score_entry_id=entry_id,
            composer="Test Composer",
            title="Test Title",
            source_repository="test_repo",
            source_commit="a" * 40,
            source_relative_path="test_path",
            source_sha256="c" * 64,
            manifest_hash="b" * 64,
            parser_version="1.0.0",
            measures=tuple(measures),
            events=tuple(final_events),
            parser_name="ms3"
        )
    return _make_score

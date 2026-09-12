"""
Unit tests for CanonicalScore, CanonicalMeasure, and CanonicalScoreEvent.
"""

from fractions import Fraction

import pytest

from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.score import (
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
    TieState,
)
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


def test_canonical_score_event_valid_note() -> None:
    pitch = SpelledPitch(letter=PitchLetter.C, alteration=1, octave=4)
    event = CanonicalScoreEvent(
        piece_id="dcml_medtner_tales:op34n02",
        event_id="evt_001",
        event_index=0,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(0, 1),
        offset_in_measure=Fraction(0, 1),
        duration=Fraction(1, 4),
        pitch=pitch,
        midi=61,
        is_grace=False,
        tie_state=TieState.NONE,
    )
    assert event.pitch == pitch
    assert event.midi == 61
    assert event.duration == Fraction(1, 4)


def test_canonical_score_event_midi_mismatch_raises() -> None:
    pitch = SpelledPitch(letter=PitchLetter.C, alteration=1, octave=4)  # MIDI 61
    with pytest.raises(ValueError, match="MIDI number mismatch"):
        CanonicalScoreEvent(
            piece_id="dcml_medtner_tales:op34n02",
            event_id="evt_001",
            event_index=0,
            event_kind=EventKind.NOTE,
            measure_index=0,
            source_measure_label="1",
            staff=1,
            voice=1,
            global_onset=Fraction(0, 1),
            offset_in_measure=Fraction(0, 1),
            duration=Fraction(1, 4),
            pitch=pitch,
            midi=60,  # Wrong!
        )


def test_canonical_score_event_rest_with_pitch_raises() -> None:
    pitch = SpelledPitch(letter=PitchLetter.C, alteration=0, octave=4)
    with pytest.raises(ValueError, match="REST event must not specify pitch"):
        CanonicalScoreEvent(
            piece_id="dcml_medtner_tales:op34n02",
            event_id="evt_001",
            event_index=0,
            event_kind=EventKind.REST,
            measure_index=0,
            source_measure_label="1",
            staff=1,
            voice=1,
            global_onset=Fraction(0, 1),
            offset_in_measure=Fraction(0, 1),
            duration=Fraction(1, 4),
            pitch=pitch,
        )


def test_canonical_score_hash_and_sorting() -> None:
    ts = TimeSignature(4, 4)
    m0 = CanonicalMeasure(
        piece_id="dcml_medtner_tales:op34n02",
        measure_index=0,
        source_measure_label="1",
        global_onset=Fraction(0, 1),
        actual_duration=Fraction(1, 1),
        time_signature=ts,
        expected_duration=Fraction(1, 1),
    )
    p_csharp = SpelledPitch(letter=PitchLetter.C, alteration=1, octave=4)
    p_dflat = SpelledPitch(letter=PitchLetter.D, alteration=-1, octave=4)

    e1 = CanonicalScoreEvent(
        piece_id="dcml_medtner_tales:op34n02",
        event_id="evt_0",
        event_index=0,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(0, 1),
        offset_in_measure=Fraction(0, 1),
        duration=Fraction(1, 4),
        pitch=p_csharp,
        midi=61,
    )
    e2 = CanonicalScoreEvent(
        piece_id="dcml_medtner_tales:op34n02",
        event_id="evt_1",
        event_index=1,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(1, 4),
        offset_in_measure=Fraction(1, 4),
        duration=Fraction(1, 4),
        pitch=p_dflat,
        midi=61,
    )

    score = CanonicalScore(
        piece_id="dcml_medtner_tales:op34n02",
        corpus_id="dcml_medtner_tales",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="op34n02",
        composer="Nikolai Medtner",
        title="Fairy Tale Op. 34 No. 2",
        source_repository="DCMLab/medtner_tales",
        source_commit="1d2e58ba8d329463829e45e75900af43be4256bf",
        source_relative_path="MS3/op34n02.mscx",
        source_sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        manifest_hash="cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212",
        parser_version="2.4.0",
        measures=(m0,),
        events=(e1, e2),
    )

    h1 = score.compute_piece_hash()
    assert len(h1) == 64

    # Require identical hash on identical re-creation
    score2 = CanonicalScore(
        piece_id="dcml_medtner_tales:op34n02",
        corpus_id="dcml_medtner_tales",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="op34n02",
        composer="Nikolai Medtner",
        title="Fairy Tale Op. 34 No. 2",
        source_repository="DCMLab/medtner_tales",
        source_commit="1d2e58ba8d329463829e45e75900af43be4256bf",
        source_relative_path="MS3/op34n02.mscx",
        source_sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        manifest_hash="cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212",
        parser_version="2.4.0",
        measures=(m0,),
        events=(e1, e2),
    )
    assert score2.compute_piece_hash() == h1


def test_canonical_score_unsorted_events_raises() -> None:
    ts = TimeSignature(4, 4)
    m0 = CanonicalMeasure(
        piece_id="dcml_medtner_tales:op34n02",
        measure_index=0,
        source_measure_label="1",
        global_onset=Fraction(0, 1),
        actual_duration=Fraction(1, 1),
        time_signature=ts,
        expected_duration=Fraction(1, 1),
    )
    p = SpelledPitch(letter=PitchLetter.C, alteration=0, octave=4)

    e_later = CanonicalScoreEvent(
        piece_id="dcml_medtner_tales:op34n02",
        event_id="evt_1",
        event_index=1,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(1, 4),
        offset_in_measure=Fraction(1, 4),
        duration=Fraction(1, 4),
        pitch=p,
        midi=60,
    )
    e_earlier = CanonicalScoreEvent(
        piece_id="dcml_medtner_tales:op34n02",
        event_id="evt_0",
        event_index=0,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(0, 1),
        offset_in_measure=Fraction(0, 1),
        duration=Fraction(1, 4),
        pitch=p,
        midi=60,
    )

    with pytest.raises(ValueError, match="Events are not deterministically sorted"):
        CanonicalScore(
            piece_id="dcml_medtner_tales:op34n02",
            corpus_id="dcml_medtner_tales",
            corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
            score_entry_id="op34n02",
            composer="Nikolai Medtner",
            title="Fairy Tale Op. 34 No. 2",
            source_repository="DCMLab/medtner_tales",
            source_commit="1d2e58ba8d329463829e45e75900af43be4256bf",
            source_relative_path="MS3/op34n02.mscx",
            source_sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            manifest_hash="cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212",
            parser_version="2.4.0",
            measures=(m0,),
            events=(e_later, e_earlier),
        )

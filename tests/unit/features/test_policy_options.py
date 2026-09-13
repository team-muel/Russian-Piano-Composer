from fractions import Fraction

from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.score import (
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
    TieState,
)
from russian_piano_composer.features import extract_piece_features
from russian_piano_composer.features.interval_features import extract_interval_features
from russian_piano_composer.features.policy import (
    FeatureExtractionPolicy,
    MelodicTransitionPolicy,
    TieAttackPolicy,
)
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


def test_tie_policy_behavior() -> None:
    """Prove tie_policy option (EXCLUDE_CONTINUATIONS vs COUNT_EVERY_EVENT) changes pitch and rhythm statistics."""
    piece_id = "test:tie_entry"
    measures = (
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )
    e1 = CanonicalScoreEvent(
        piece_id=piece_id,
        event_id=f"{piece_id}:evt_0",
        event_index=0,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(0),
        offset_in_measure=Fraction(0),
        duration=Fraction(1, 4),
        pitch=SpelledPitch(PitchLetter.C, 0, 4),
        midi=60,
        tie_state=TieState.START,
    )
    e2 = CanonicalScoreEvent(
        piece_id=piece_id,
        event_id=f"{piece_id}:evt_1",
        event_index=1,
        event_kind=EventKind.NOTE,
        measure_index=0,
        source_measure_label="1",
        staff=1,
        voice=1,
        global_onset=Fraction(1, 4),
        offset_in_measure=Fraction(1, 4),
        duration=Fraction(1, 4),
        pitch=SpelledPitch(PitchLetter.C, 0, 6),
        midi=84,  # C6 pitch continuation event
        tie_state=TieState.CONTINUE,
    )
    score = CanonicalScore(
        piece_id=piece_id,
        corpus_id="test",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="tie_entry",
        composer="T",
        title="T",
        source_repository="t",
        source_commit="a" * 40,
        source_relative_path="a.mscx",
        source_sha256="0" * 64,
        manifest_hash="b" * 64,
        parser_version="1.0",
        measures=measures,
        events=(e1, e2),
    )

    policy_exclude = FeatureExtractionPolicy(tie_policy=TieAttackPolicy.EXCLUDE_CONTINUATIONS)
    policy_count_all = FeatureExtractionPolicy(tie_policy=TieAttackPolicy.COUNT_EVERY_EVENT)

    res_exclude = extract_piece_features(score, manifest_hash="abc", policy=policy_exclude)
    res_count_all = extract_piece_features(score, manifest_hash="abc", policy=policy_count_all)

    # Under EXCLUDE_CONTINUATIONS, event 2 is omitted: pitch_highest_midi = 60
    # Under COUNT_EVERY_EVENT, event 2 is counted: pitch_highest_midi = 84
    assert res_exclude.features["pitch_highest_midi"] == 60
    assert res_count_all.features["pitch_highest_midi"] == 84


def test_melodic_policy_behavior() -> None:
    """Prove melodic_policy option (VOICE_AWARE vs GLOBAL_ONSET_SORTED) changes extracted interval statistics."""
    piece_id = "test:e"
    measures = (
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )

    # Voice 1: C4 (60) at onset 0 -> D4 (62) at onset 1/4 (interval = +2)
    # Voice 2: C6 (84) at onset 0 -> D6 (86) at onset 1/4 (interval = +2)
    e1_v1 = CanonicalScoreEvent(piece_id=piece_id, event_id="1", event_index=0, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 4), pitch=SpelledPitch(PitchLetter.C, 0, 4), midi=60)
    e1_v2 = CanonicalScoreEvent(piece_id=piece_id, event_id="3", event_index=1, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=2, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 4), pitch=SpelledPitch(PitchLetter.C, 0, 6), midi=84)

    e2_v1 = CanonicalScoreEvent(piece_id=piece_id, event_id="2", event_index=2, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(1, 4), offset_in_measure=Fraction(1, 4), duration=Fraction(1, 4), pitch=SpelledPitch(PitchLetter.D, 0, 4), midi=62)
    e2_v2 = CanonicalScoreEvent(piece_id=piece_id, event_id="4", event_index=3, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=2, global_onset=Fraction(1, 4), offset_in_measure=Fraction(1, 4), duration=Fraction(1, 4), pitch=SpelledPitch(PitchLetter.D, 0, 6), midi=86)

    score = CanonicalScore(piece_id=piece_id, corpus_id="test", corpus_role=CorpusRole.GENERATIVE_RUSSIAN, score_entry_id="e", composer="T", title="T", source_repository="t", source_commit="a"*40, source_relative_path="a.mscx", source_sha256="0"*64, manifest_hash="b"*64, parser_version="1.0", measures=measures, events=(e1_v1, e1_v2, e2_v1, e2_v2))

    policy_voice_aware = FeatureExtractionPolicy(melodic_policy=MelodicTransitionPolicy.VOICE_AWARE_SINGLE_NOTE_ONLY)
    policy_global = FeatureExtractionPolicy(melodic_policy=MelodicTransitionPolicy.GLOBAL_ONSET_SORTED)

    res_voice_aware = extract_interval_features(score, policy=policy_voice_aware)
    res_global = extract_interval_features(score, policy=policy_global)

    # In voice aware mode, each voice has 1 note at onset 0 and 1 note at onset 1/4 -> intervals +2, +2. Max abs = 2.
    assert res_voice_aware["interval_max_abs_semitones"] == 2

    # In global mode, onset 0 has 2 notes (60, 84) and onset 1/4 has 2 notes (62, 86).
    # Since require_single_note_voice defaults to True, len(group) == 2 means 0 eligible transitions in global mode!
    assert res_global["interval_max_abs_semitones"] is None


def test_require_single_note_voice_behavior() -> None:
    """Prove require_single_note_voice option changes extraction output when chords occur within a voice."""
    piece_id = "test:s"
    measures = (
        CanonicalMeasure(
            piece_id=piece_id,
            measure_index=0,
            source_measure_label="1",
            global_onset=Fraction(0),
            actual_duration=Fraction(1),
            time_signature=TimeSignature(4, 4),
            expected_duration=Fraction(1),
        ),
    )

    # Dyad (60, 64) at onset 0 -> Dyad (62, 67) at onset 1/4 in staff 1 voice 1
    e1 = CanonicalScoreEvent(piece_id=piece_id, event_id="1", event_index=0, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 4), pitch=SpelledPitch(PitchLetter.C, 0, 4), midi=60)
    e2 = CanonicalScoreEvent(piece_id=piece_id, event_id="2", event_index=1, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(0), offset_in_measure=Fraction(0), duration=Fraction(1, 4), pitch=SpelledPitch(PitchLetter.E, 0, 4), midi=64)

    e3 = CanonicalScoreEvent(piece_id=piece_id, event_id="3", event_index=2, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(1, 4), offset_in_measure=Fraction(1, 4), duration=Fraction(1, 4), pitch=SpelledPitch(PitchLetter.D, 0, 4), midi=62)
    e4 = CanonicalScoreEvent(piece_id=piece_id, event_id="4", event_index=3, event_kind=EventKind.NOTE, measure_index=0, source_measure_label="1", staff=1, voice=1, global_onset=Fraction(1, 4), offset_in_measure=Fraction(1, 4), duration=Fraction(1, 4), pitch=SpelledPitch(PitchLetter.G, 0, 4), midi=67)

    score = CanonicalScore(piece_id=piece_id, corpus_id="test", corpus_role=CorpusRole.GENERATIVE_RUSSIAN, score_entry_id="s", composer="T", title="T", source_repository="t", source_commit="a"*40, source_relative_path="a.mscx", source_sha256="0"*64, manifest_hash="b"*64, parser_version="1.0", measures=measures, events=(e1, e2, e3, e4))

    policy_strict = FeatureExtractionPolicy(require_single_note_voice=True)
    policy_permissive = FeatureExtractionPolicy(require_single_note_voice=False)

    res_strict = extract_interval_features(score, policy=policy_strict)
    res_permissive = extract_interval_features(score, policy=policy_permissive)

    # Under require_single_note_voice=True, chord onsets are skipped -> None
    assert res_strict["interval_mean_abs_semitones"] is None

    # Under require_single_note_voice=False, chord onsets are averaged: avg(60,64)=62 -> avg(62,67)=64.5 -> round(64.5-62) = 2 or 3
    assert res_permissive["interval_mean_abs_semitones"] is not None

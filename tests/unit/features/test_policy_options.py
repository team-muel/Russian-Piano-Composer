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
from russian_piano_composer.features.policy import (
    FeatureExtractionPolicy,
    GraceNotePolicy,
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


def test_grace_policy_behavior() -> None:
    """Prove grace_policy option (EXCLUDE vs INCLUDE) changes extracted feature values."""
    piece_id = "test:grace_entry"
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
        duration=Fraction(0),
        pitch=SpelledPitch(PitchLetter.C, 0, 6),
        midi=84,  # High C6 grace note
        is_grace=True,
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
        global_onset=Fraction(0),
        offset_in_measure=Fraction(0),
        duration=Fraction(1, 4),
        pitch=SpelledPitch(PitchLetter.C, 0, 4),
        midi=60,
    )
    score = CanonicalScore(
        piece_id=piece_id,
        corpus_id="test",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="grace_entry",
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

    policy_exclude = FeatureExtractionPolicy(grace_policy=GraceNotePolicy.EXCLUDE)
    policy_include = FeatureExtractionPolicy(grace_policy=GraceNotePolicy.INCLUDE)

    res_exclude = extract_piece_features(score, manifest_hash="abc", policy=policy_exclude)
    res_include = extract_piece_features(score, manifest_hash="abc", policy=policy_include)

    assert res_exclude.features["pitch_highest_midi"] == 60
    assert res_include.features["pitch_highest_midi"] == 84


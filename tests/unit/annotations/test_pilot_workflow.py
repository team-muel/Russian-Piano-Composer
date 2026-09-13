"""
Unit and regression tests for RC-008B length-stratified pilot selection, role-blind packets,
anti-self-acceptance invariants, lineage binding, and semantic hashing.
"""
from fractions import Fraction
from pathlib import Path

import pytest
import yaml

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.corpus.theme_annotations import (
    accepted_annotations,
    generative_training_annotations,
    load_theme_annotation_manifest,
)
from russian_piano_composer.domain.annotations import (
    AnnotationStatus,
    AnnotatorType,
    ReviewDecision,
    ReviewerType,
    ReviewRecord,
    ScorePosition,
    ThemeAnnotation,
    ThemeRole,
    ThemeSpan,
)


def test_pilot_selection_manifest_properties() -> None:
    selection_file = Path("data/annotations/theme_v1/pilot_selection_v1.yaml")
    assert selection_file.exists(), "Pilot selection manifest file must exist."

    with open(selection_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["pilot_id"] == "rc008b_pilot_v1"
    assert data["selection_version"] == 1
    assert data["canonical_schema_version"] == 1
    assert "pilot_selection_hash" in data
    assert len(data["selected_piece_ids"]) == 18, "Exactly 18 pieces must be selected (3 per corpus)."

    pieces = data["pieces"]
    assert len(pieces) == 18

    # Verify exactly 3 pieces per corpus across 6 corpora
    by_corpus: dict[str, list[dict]] = {}
    for p in pieces:
        by_corpus.setdefault(p["corpus_id"], []).append(p)

    assert len(by_corpus) == 6, "Must have selected pieces from all 6 corpora."
    for corpus_id, p_list in by_corpus.items():
        assert len(p_list) == 3, f"Corpus {corpus_id} must have exactly 3 selected pieces."
        strata = {p["selection_stratum"] for p in p_list}
        assert strata == {"SHORT", "MEDIUM", "LONG"}, f"Corpus {corpus_id} must cover SHORT, MEDIUM, and LONG strata."


def test_role_blind_packets() -> None:
    selection_file = Path("data/annotations/theme_v1/pilot_selection_v1.yaml")
    with open(selection_file, encoding="utf-8") as f:
        sel_data = yaml.safe_load(f)

    sel_hash = sel_data["pilot_selection_hash"]
    packets_dir = Path("data/interim/theme_annotation_packets") / sel_hash
    if packets_dir.exists():
        packet_files = list(packets_dir.glob("*/packet.yaml"))
        assert len(packet_files) == 18, "Must generate 18 role-blind packet files."

        for p_file in packet_files:
            with open(p_file, encoding="utf-8") as f:
                pkt = yaml.safe_load(f)
            assert pkt["role_blind"] is True
            # Verify that role (e.g. GENERATIVE_RUSSIAN or CONTROL_NON_RUSSIAN) is NOT in annotator packet metadata
            assert "corpus_role" not in pkt
            assert "role" not in pkt



def test_ai_candidate_cannot_be_accepted_regression() -> None:
    candidates_file = Path("data/annotations/theme_v1/pilots/rc008b/candidates.yaml")
    assert candidates_file.exists(), "Pilot candidates manifest must exist."

    pilot_set = load_theme_annotation_manifest(candidates_file)
    assert len(pilot_set.annotations) == 20

    # Verify that all AI-created candidate annotations have status != ACCEPTED
    for ann in pilot_set.annotations:
        assert ann.annotator_type == AnnotatorType.ALGORITHM_CANDIDATE
        assert ann.status != AnnotationStatus.ACCEPTED
        assert ann.status in (AnnotationStatus.REVIEWED, AnnotationStatus.CANDIDATE, AnnotationStatus.DISPUTED)

    # CRITICAL INVARIANT: Accepted count must be 0
    accepted = accepted_annotations(pilot_set)
    assert len(accepted) == 0

    # CRITICAL INVARIANT: Generative training count must be 0
    manifest = load_manifest("data/manifests/corpus_manifest.yaml")
    gen_train = generative_training_annotations(pilot_set, manifest)
    assert len(gen_train) == 0


def test_ai_candidate_forced_to_accepted_raises_error() -> None:
    span = ThemeSpan(ScorePosition(0, Fraction(0)), ScorePosition(8, Fraction(0)))
    ai_review = ReviewRecord(
        reviewer_id="ai_rev",
        reviewer_type=ReviewerType.AI_REVIEWER,
        decision=ReviewDecision.APPROVE,
    )

    # Attempting to force an ALGORITHM_CANDIDATE proposal to ACCEPTED status MUST raise ValueError
    with pytest.raises(ValueError, match="ALGORITHM_CANDIDATE proposals cannot have status ACCEPTED"):
        ThemeAnnotation(
            annotation_id="ann_forced",
            piece_id="p1",
            corpus_id="c1",
            score_entry_id="s1",
            span=span,
            theme_role=ThemeRole.PRIMARY_THEME,
            confidence=3,
            status=AnnotationStatus.ACCEPTED,
            annotator_id="algo_bot",
            annotator_type=AnnotatorType.ALGORITHM_CANDIDATE,
            reviews=(ai_review,),
        )


def test_legitimate_human_approval_path() -> None:
    span = ThemeSpan(ScorePosition(0, Fraction(0)), ScorePosition(8, Fraction(0)))
    human_review = ReviewRecord(
        reviewer_id="human_expert_1",
        reviewer_type=ReviewerType.SECOND_HUMAN_REVIEW,
        decision=ReviewDecision.APPROVE,
        notes="Human expert approval.",
    )

    ann_human = ThemeAnnotation(
        annotation_id="ann_human_ok",
        piece_id="p1",
        corpus_id="c1",
        score_entry_id="s1",
        span=span,
        theme_role=ThemeRole.PRIMARY_THEME,
        confidence=3,
        status=AnnotationStatus.ACCEPTED,
        annotator_id="human_author",
        annotator_type=AnnotatorType.HUMAN,
        reviews=(human_review,),
    )
    assert ann_human.status == AnnotationStatus.ACCEPTED

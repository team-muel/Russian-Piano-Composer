"""
Property-based tests for CTU discovery and validation invariants.
"""


from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy
from russian_piano_composer.ctu.representation import extract_segment_representation
from russian_piano_composer.ctu.similarity import compute_segment_similarity
from tests.unit.ctu.test_ctu_fixtures import _build_test_score


def test_ctu_determinism_property() -> None:
    """Property Test — Discovering CTUs on the same score twice returns identical candidates and hashes."""
    midis = {0: [60, 62, 64], 2: [60, 62, 64]}
    score = _build_test_score("test:det", 16, midis)
    policy = CTUDiscoveryPolicy()

    res1 = discover_ctus_for_score(score, manifest_hash="abc", policy=policy)
    res2 = discover_ctus_for_score(score, manifest_hash="abc", policy=policy)

    assert res1.raw_candidate_count == res2.raw_candidate_count
    assert res1.post_dedup_candidate_count == res2.post_dedup_candidate_count
    assert [c.candidate_id for c in res1.retained_ctus] == [c.candidate_id for c in res2.retained_ctus]


def test_similarity_symmetry_property() -> None:
    """Property Test — Sim(A, B) == Sim(B, A) strictly holds."""
    midis1 = {0: [60, 62, 64, 65]}
    midis2 = {0: [67, 69, 71, 72]}
    score1 = _build_test_score("test:sym1", 16, midis1)
    score2 = _build_test_score("test:sym2", 16, midis2)

    from russian_piano_composer.ctu.models import SegmentPosition, SegmentSpan
    span = SegmentSpan(SegmentPosition(0), SegmentPosition(1))
    rep1 = extract_segment_representation(score1, span)
    rep2 = extract_segment_representation(score2, span)

    assert compute_segment_similarity(rep1, rep2) == compute_segment_similarity(rep2, rep1)


def test_reordered_motif_distinguishable_property() -> None:
    """Property Test — Ordered n-gram multiset similarity distinguishes reordered motifs."""
    score1 = _build_test_score("test:ord1", 16, {0: [60, 62, 64, 67]})
    score2 = _build_test_score("test:ord2", 16, {0: [67, 64, 62, 60]})  # Retrograde order

    from russian_piano_composer.ctu.models import SegmentPosition, SegmentSpan
    span = SegmentSpan(SegmentPosition(0), SegmentPosition(1))
    rep1 = extract_segment_representation(score1, span)
    rep2 = extract_segment_representation(score2, span)

    sim = compute_segment_similarity(rep1, rep2)
    # Reordered interval sequence: (+2, +2, +3) vs (-3, -2, -2) -> 2-gram multiset intersection is 0,
    # but rhythm ratios and pitch-class histogram overlap partially -> composite similarity is ~0.60 vs 1.0 for exact match
    assert sim < 0.80


def test_empty_missing_channel_property() -> None:
    """Property Test — Missing/empty evidence channels do not yield 1.0 similarity."""
    score1 = _build_test_score("test:emp1", 16, {0: []})
    score2 = _build_test_score("test:emp2", 16, {0: []})

    from russian_piano_composer.ctu.models import SegmentPosition, SegmentSpan
    span = SegmentSpan(SegmentPosition(0), SegmentPosition(1))
    rep1 = extract_segment_representation(score1, span)
    rep2 = extract_segment_representation(score2, span)

    # Sparse/degenerate segments return 0.0 because available weight < 0.20
    assert compute_segment_similarity(rep1, rep2) == 0.0


def test_hash_sensitivity_properties() -> None:
    """Property Test — Mutating policy fields alters computed policy hashes."""
    p1 = CTUDiscoveryPolicy(weight_melodic=0.40)
    p2 = CTUDiscoveryPolicy(weight_melodic=0.50)
    assert p1.compute_policy_hash() != p2.compute_policy_hash()

    from russian_piano_composer.ctu.models import (
        compute_ctu_schema_semantic_hash,
        compute_segment_representation_semantic_hash,
        compute_similarity_semantic_hash,
    )
    assert len(compute_ctu_schema_semantic_hash()) == 64
    assert len(compute_segment_representation_semantic_hash()) == 64
    assert len(compute_similarity_semantic_hash()) == 64

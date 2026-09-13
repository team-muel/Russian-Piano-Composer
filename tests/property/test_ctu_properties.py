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


def test_global_transposition_invariance_property() -> None:
    """Property Test — Transposing pitches globally preserves multi-channel relative similarity."""
    midis_orig = {0: [60, 62, 64, 65], 2: [67, 69, 71, 72]}
    midis_trans = {0: [67, 69, 71, 72], 2: [74, 76, 78, 79]}

    score1 = _build_test_score("test:t1", 16, midis_orig)
    score2 = _build_test_score("test:t2", 16, midis_trans)

    from russian_piano_composer.ctu.models import SegmentPosition, SegmentSpan
    span1 = SegmentSpan(SegmentPosition(0), SegmentPosition(1))
    span2 = SegmentSpan(SegmentPosition(2), SegmentPosition(3))

    rep1_orig = extract_segment_representation(score1, span1)
    rep2_orig = extract_segment_representation(score1, span2)

    rep1_trans = extract_segment_representation(score2, span1)
    rep2_trans = extract_segment_representation(score2, span2)

    sim_orig = compute_segment_similarity(rep1_orig, rep2_orig)
    sim_trans = compute_segment_similarity(rep1_trans, rep2_trans)

    assert sim_orig == sim_trans

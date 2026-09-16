"""
Unsupervised CTU discovery engine and non-maximum suppression (NMS) deduplication.
"""

import hashlib

from russian_piano_composer.ctu.models import (
    CTUCandidate,
    CTUDiscoveryResult,
    EvidenceTier,
)
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy
from russian_piano_composer.ctu.representation import extract_segment_representation
from russian_piano_composer.ctu.segmentation import (
    compute_temporal_split,
    generate_candidate_spans,
)
from russian_piano_composer.ctu.similarity import (
    compute_segment_similarity,
    compute_span_jaccard_overlap,
    spans_overlap,
)
from russian_piano_composer.domain.score import CanonicalScore


def discover_ctus_for_score(
    score: CanonicalScore,
    manifest_hash: str,
    policy: CTUDiscoveryPolicy | None = None,
) -> CTUDiscoveryResult:
    """
    Perform unsupervised CTU candidate generation, recurrence scoring, and NMS deduplication
    strictly within the discovery region of a single canonical score.

    Note: Control generation is separate and performed during validation via build_matched_control_pairs.
    """
    if policy is None:
        policy = CTUDiscoveryPolicy()

    policy_hash = policy.compute_policy_hash()
    piece_hash = score.compute_piece_hash()
    discovery_measures, total_measures, is_eligible = compute_temporal_split(score, policy=policy)

    if not is_eligible or discovery_measures == 0:
        return CTUDiscoveryResult(
            piece_id=score.piece_id,
            corpus_id=score.corpus_id,
            canonical_piece_hash=piece_hash,
            total_measures=total_measures,
            discovery_measures=discovery_measures,
            is_eligible=False,
            retained_ctus=(),
            raw_candidate_count=0,
            post_dedup_candidate_count=0,
            manifest_hash=manifest_hash,
            discovery_policy_hash=policy_hash,
        )

    # 1. Generate candidate spans within discovery region
    spans = generate_candidate_spans(score, discovery_measures, policy=policy)
    raw_count = len(spans)

    if raw_count == 0:
        return CTUDiscoveryResult(
            piece_id=score.piece_id,
            corpus_id=score.corpus_id,
            canonical_piece_hash=piece_hash,
            total_measures=total_measures,
            discovery_measures=discovery_measures,
            is_eligible=True,
            retained_ctus=(),
            raw_candidate_count=0,
            post_dedup_candidate_count=0,
            manifest_hash=manifest_hash,
            discovery_policy_hash=policy_hash,
        )

    # 2. Extract representations for all candidate spans
    representations = [extract_segment_representation(score, span) for span in spans]

    # 3. Compute pairwise recurrence similarity against non-overlapping discovery segments
    discovery_scores: list[float] = []
    for i, (span1, rep1) in enumerate(zip(spans, representations, strict=True)):
        non_overlap_sims: list[float] = []
        for j, (span2, rep2) in enumerate(zip(spans, representations, strict=True)):
            if i != j and not spans_overlap(span1, span2):
                sim = compute_segment_similarity(rep1, rep2, policy=policy)
                non_overlap_sims.append(sim)

        max_recurrence = max(non_overlap_sims) if non_overlap_sims else 0.0
        discovery_scores.append(max_recurrence)

    # 4. Build candidate list sorted by discovery score descending
    candidates: list[CTUCandidate] = []
    for _idx, (span, rep, score_val) in enumerate(zip(spans, representations, discovery_scores, strict=True)):
        rep_hash = rep.compute_content_hash()
        cid_input = f"{score.piece_id}|{span.start.measure_index}|{span.end.measure_index}|{rep_hash}".encode()
        cand_id = f"ctu_{hashlib.sha256(cid_input).hexdigest()[:16]}"
        tier = EvidenceTier.E1_DISCOVERY_RECURRENCE if score_val >= policy.evidence_threshold_e1 else EvidenceTier.E0_CANDIDATE_ONLY

        candidates.append(
            CTUCandidate(
                candidate_id=cand_id,
                piece_id=score.piece_id,
                corpus_id=score.corpus_id,
                canonical_piece_hash=piece_hash,
                span=span,
                representation=rep,
                discovery_score=score_val,
                tier=tier,
                representation_hash=rep_hash,
                discovery_policy_hash=policy_hash,
                manifest_hash=manifest_hash,
            )
        )

    candidates.sort(key=lambda c: (-c.discovery_score, c.span.start.measure_index, c.span.end.measure_index))

    # 5. Non-Maximum Suppression (NMS) Deduplication
    retained: list[CTUCandidate] = []
    for cand in candidates:
        overlap_found = False
        for prev in retained:
            if compute_span_jaccard_overlap(cand.span, prev.span) >= policy.nms_overlap_threshold:
                overlap_found = True
                break
        if not overlap_found:
            retained.append(cand)
            if len(retained) >= policy.max_retained_ctus:
                break

    post_dedup_count = len(retained)

    return CTUDiscoveryResult(
        piece_id=score.piece_id,
        corpus_id=score.corpus_id,
        canonical_piece_hash=piece_hash,
        total_measures=total_measures,
        discovery_measures=discovery_measures,
        is_eligible=True,
        retained_ctus=tuple(retained),
        raw_candidate_count=raw_count,
        post_dedup_candidate_count=post_dedup_count,
        manifest_hash=manifest_hash,
        discovery_policy_hash=policy_hash,
    )

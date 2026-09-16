# ADR-009 — Unsupervised CTU Discovery & Held-Out Validation Architecture

## Status

Accepted

## Context

Previous milestones established canonical score ingestion (RC-001 through RC-007), pilot human theme adjudication (RC-008B), and feature validity auditing (RC-009A). To assess whether computational symbolic thematic units exhibit genuine future recurrence and developmental reuse across polyphonic piano literature without relying on human theme labels, an unsupervised candidate discovery and temporal held-out validation architecture is required.

## Decision

1. **Operational CTU Definition**: CTUs are defined as computational operational objects (`CTUCandidate`), completely independent of human theme annotations or composer metadata.
2. **Temporal Split Anti-Leakage**: Chronologically partition each piece into a 60% Discovery Region and a 40% Future Validation Region. Candidate generation, representation, and ranking take place strictly within the Discovery Region.
3. **Multi-Scale Candidate Windows**: Generate candidates at 1, 2, 3, 4, 6, and 8 measure window lengths with 1-measure stride.
4. **Polyphonic Multi-Channel Representation**: Maintain separate, un-flattened evidence channels for melodic streams `(staff, voice)`, IOI rhythmic ratios ($r_i = \text{IOI}_{i+1}/\text{IOI}_i$), texture profiles, and pitch-class distributions.
5. **Decoupled Control Generation & Fail-Closed Pairing**: Control generation is governed strictly by `CTUValidationPolicy` in `build_matched_control_pairs()`. Unmatched CTUs (`CONTROL_UNAVAILABLE`) are excluded from both CTU and control averages.
6. **Mathematical Activity Matching**: Controls must satisfy exact relative ratio tolerances ($| \text{cand} - \text{target} | / \text{target} \le 0.25$) for attack count and onset count without integer rounding approximations.
7. **Sparse Sequence Similarity Semantics**: Formally frozen as ordered 2-gram multiset Jaccard with single-element 1-gram fallback.
8. **Validation Semantic Hashing**: Algorithmic validation semantics are hashed into `validation_semantic_hash` separate from tunable policy values.
9. **Piece-Level Statistical Aggregation**: Aggregate CTU vs control future-reuse metrics at the piece level to prevent pseudoreplication before performing corpus-level paired permutation testing and bootstrap confidence interval estimation.

## Consequences

* Ensures zero temporal or annotation leakage during candidate discovery.
* Enforces fail-closed, activity-matched negative control pairs.
* Provides deterministic, two-process reproducible lineage hashes across the 141-piece canonical corpus.
* Establishes a frozen V1 pipeline for unsupervised thematic discovery.

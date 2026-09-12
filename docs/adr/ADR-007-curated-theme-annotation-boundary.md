# ADR-007: Curated Theme Annotation Boundaries, Review State Machine, and Lineage Binding

## Context
Symbolic score analysis and theme generation require ground-truth thematic annotations across Russian late-Romantic and non-Russian control piano corpora. Silently equating arbitrary melodic fragments or algorithmic proposals with thematic truth invalidates scientific rigor. Furthermore, canonical score representations may evolve, risking annotation coordinate drift.

## Decision
1. **Half-Open Canonical Coordinates**:
   Use exact rational score coordinates `ScorePosition(measure_index, offset)` with half-open interval $[start, end)$ semantics.
2. **Flexible Historical Theme Lengths**:
   Historical thematic statements will be annotated at their full defensible musical length (whether 2, 4, 8, or 16 bars) without artificial truncation to 2–4 bar generator constraints.
3. **Immutable Review State Machine & Anti-Self-Acceptance**:
   Annotations undergo explicit review (`CANDIDATE`, `REVIEWED`, `ACCEPTED`, `DISPUTED`, `REJECTED`, `STALE`). Algorithmic proposals (`ALGORITHM_CANDIDATE`) can never self-accept without independent human approval.
4. **Fail-Closed Lineage Binding**:
   Annotations bind directly to the canonical piece SHA-256 semantic hash (`canonical_piece_hash`) and corpus manifest hash (`manifest_hash`). Any change to underlying score data invalidates annotations into `STALE` status.
5. **Rights & Generative Isolation**:
   Generative training selection requires `ACCEPTED` status, `confidence >= 2`, `GENERATIVE_RUSSIAN` role, AND `generative_eligible == True`. Control corpora and unapproved Russian corpora remain isolated from training.

## Consequences
- Prevents invalid algorithmic candidate self-acceptance.
- Protects dataset against silent coordinate corruption upon score re-parsing.
- Maintains strict scientific separation between research analysis and legal generative training eligibility.

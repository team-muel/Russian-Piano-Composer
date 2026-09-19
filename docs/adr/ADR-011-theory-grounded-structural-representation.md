# ADR-011: Theory-Grounded Structural Music Representation Foundation

## Status
ACCEPTED

## Context
Following the formal closure and acceptance of RC-009A (Piece-Level Representation), RC-009B (CTU Unsupervised Discovery & Validation, status: `CTU_VALIDATED`), and RC-010 (Composer-Held-Out Style Discrimination, status: `RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED`), the project required a comprehensive, theory-grounded symbolic music representation foundation prior to any generative composition attempts.

RC-010 proved that shallow surface-level stylistic markers and statistical n-grams alone do not support reliable composer-held-out generalisation across the current Russian vs. Control corpora without risking overinterpretation. Generative modeling therefore requires deep, structural musical features grounded in music theory and cognitive musicology.

## Decision
We implemented **`STRUCTURAL_REPRESENTATION_SCHEMA_V1`**, a frozen 56-feature structural representation across 7 core musical families:

1. **Family A: Tonal / Harmonic Center Proxies** (8 features) — Duration-weighted pitch-class distributions, Krumhansl-Kessler key correlations, local sliding window key centers, circle-of-fifths distances, and chromatic duration shares.
2. **Family B: Sonority & Harmonic Motion** (8 features) — Sounding pitch-class set cardinalities, interval class vectors (IC1 semitones, IC6 tritones), bass-relative intervals, sonority transition rates, and harmonic rhythm volatility.
3. **Family C: Cadential & Boundary Proxies** (6 features) — Observable boundary candidates (IOI lengthening, metric weight), bass degree resolutions ($\hat{5}\to\hat{1}$, $\hat{7}\to\hat{1}$), dominant-to-tonic sonority resolutions, deceptive motions ($\hat{5}\to\hat{6}$), and composite resolution strengths.
4. **Family D: Formal Recurrence & Sectional Architecture** (8 features) — Self-similarity matrices (SSM), Foote novelty curves/peaks, late formal return proxies (ABA recapitulation), recurrence distances, and CTU-derived positional recurrence features.
5. **Family E: Voice-Leading Geometry** (8 features) — Outer-voice contrapuntal motion classification (parallel, contrary, oblique), soprano/bass stepwise resolutions, half-step melodic approaches, common-tone retention, and minimal voice-leading displacement (Tymoczko metric).
6. **Family F: Piano Texture & Registral Architecture** (10 features) — Registral centroids and dispersions, vertical spans, interstaff gaps, simultaneity attack counts, block chord shares, figurative arpeggiation rates, octave doublings, and repeated-note attacks.
7. **Family G: Normalized Temporal Trajectories** (8 features) — Normalized 8-bin score trajectories capturing linear slopes of register, span, density, chromaticity, cardinality, quadratic density curvature, and early-late contrast.

### Key Governance Principles
- **Strict Label-Blindness**: Feature extraction operates strictly on notation and symbolic score geometry without awareness of composer nationality, corpus roles (`GENERATIVE_RUSSIAN`, `CONTROL_NON_RUSSIAN`), or classifier weights.
- **Pre-Registration**: Complete mathematical formulas, schemas, policies, and metamorphic contracts were committed (`ad3299e0f36f4fb028a2f5125a88b19361504d27`) prior to executing corpus extraction.
- **Explicit Missingness**: Features return explicit `AvailabilityStatus` (`AVAILABLE`, `STRUCTURAL_ZERO`, `UNAVAILABLE`) with zero silent zero imputation.
- **Metamorphic Validation**: Validated against 20 synthetic test fixtures with 100% pass rate across deterministic mathematical assertions and pitch transposition invariances.

## Consequences
- 141 of 141 canonical scores in the corpus are fully represented across the 56 structural features.
- Zero style/label leakage exists across the extraction modules.
- The resulting representation provides the structural foundation for both generative constraints (RC-013+) and confirmatory structural comparison (RC-012).

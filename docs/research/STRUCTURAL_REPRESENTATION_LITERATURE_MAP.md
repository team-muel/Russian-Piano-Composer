# Structural Music Representation Literature & Theory Mapping (RC-011)

## 1. Executive Overview & Ontological Stance

RC-011 establishes a deterministic, theory-grounded structural representation of symbolic piano scores.
In accordance with scientific integrity guidelines:
- We **distinguish direct observables from inferred proxies**.
- We **do not claim categorical ground truth** (e.g., "true key", "true cadence", "true phrase") from heuristic detectors in complex 19th-century repertoire.
- Every construct documents its musicological rationale, operational definition, provenance, known ambiguities, and failure modes.

### Provenance Classification:
1. **`OBSERVED`**: Directly measurable from the score graph without model assumptions (e.g., pitch-class sets, sounding cardinality, onset intervals).
2. **`LITERATURE`**: Directly implemented from published, peer-reviewed computational musicology literature with frozen numerical profiles or algorithms.
3. **`HYPOTHESIS`**: Conceptually grounded in music-theoretic traditions (e.g., Schenkerian outer-voice framework, Caplinian formal functions) operationalized as explicit heuristic proxies.
4. **`ENGINEERING_HEURISTIC`**: Algorithmic proxies designed for robust symbolic extraction (e.g., novelty curves, temporal trajectory slopes).

---

## 2. Family A — Tonal / Harmonic Center Proxies

### 2.1 Tonal Center Estimation (Global & Local)
- **Construct**: `TONAL_CENTER_PROXY`, `LOCAL_TONAL_CENTER_PROXY`, `TONAL_STABILITY_PROXY`
- **Musicological Motivation**: Tonal music organizes pitch hierarchies around tonic pitch classes. 19th-century piano music features local key excursions, chromaticism, and circle-of-fifths navigations.
- **Literature Reference**:
  - Krumhansl, C. L., & Kessler, E. J. (1982). *Tracing the dynamic changes in perceived tonal organization in a spatial representation of musical keys*. Psychological Review, 89(4), 334-368.
  - Temperley, D. (1999). *What's key for key? The Krumhansl-Schmuckler key-finding algorithm reconsidered*. Music Perception, 17(1), 65-100.
- **Directly Observed**: Duration-weighted pitch-class distributions $D \in \mathbb{R}^{12}$.
- **Inferred Proxy**: Pearson correlation $r(D, P_{k,m})$ between pitch-class distribution and frozen Krumhansl-Kessler key profiles for 24 major/minor keys. Maximum correlation defines the tonal center proxy; difference between best and runner-up defines confidence/stability.
- **Known Failure Modes & Ambiguities**: Highly chromatic, octatonic, or whole-tone passages (common in late Romantic piano literature) produce low correlation confidence across all keys. Modulations within local windows can blur distributions.

---

## 3. Family B — Sonority & Harmonic Motion

### 3.1 Vertical Pitch-Class Sets & Interval-Class Vectors
- **Construct**: `SONORITY_PITCHCLASS_CARDINALITY`, `SONORITY_INTERVAL_CLASS_VECTOR`, `SONORITY_CHANGE_RATE`
- **Musicological Motivation**: Harmonic palette is characterized by sonority density, dissonant interval content (semitones, tritones), and harmonic tempo.
- **Literature Reference**:
  - Forte, A. (1973). *The Structure of Atonal Music*. Yale University Press. (Interval-class vector concepts applied descriptively).
  - Tymoczko, D. (2011). *A Geometry of Music: Harmony and Counterpoint in the Extended Common Practice*. Oxford University Press.
- **Directly Observed**: Sounding pitch-class simultaneities at note onsets (including sustained notes).
- **Inferred Proxy**: Equivalence partitioning under pitch-class transposition/inversion (or raw pitch-class sets) and minimal voice-leading step distances between successive sonorities.
- **Known Failure Modes**: Non-harmonic tones (passing tones, suspensions) increase apparent sonority cardinality unless filtered; RC-011 analyzes raw sounding sonorities without subjective reduction.

---

## 4. Family C — Cadential & Boundary Proxies

### 4.1 Boundary Detection & Cadential Resolutions
- **Construct**: `BOUNDARY_CANDIDATE_PROXY`, `CADENTIAL_TONIC_RESOLUTION_PROXY`, `CADENTIAL_DECEPTIVE_PROXY`
- **Musicological Motivation**: Phrase boundaries and formal joints are articulated by rhythmic deceleration, texture release, metric position, and harmonic closure.
- **Literature Reference**:
  - Caplin, W. E. (1998). *Classical Form: A Theory of Formal Functions for the Instrumental Music of Haydn, Mozart, and Beethoven*. Oxford University Press.
  - Temperley, D. (2001). *The Cognition of Basic Musical Structures*. MIT Press.
- **Directly Observed**: Inter-onset intervals (IOI), duration lengthening, rest occurrences, lowest sounding pitch (bass), metric measure positions.
- **Inferred Proxy**: Local boundary candidate score combining durational lengthening and rest presence, evaluated alongside bass motion ($\hat{5} \to \hat{1}$, $\hat{5} \to \hat{6}$) relative to local tonal center proxy.
- **Known Failure Modes**: Romantic elided cadences, deceptive resolutions, and continuous virtuoso accompaniment textures can mask boundary cues.

---

## 5. Family D — Formal Recurrence & Sectional Architecture

### 5.1 Self-Similarity Matrices, Novelty Curves & Return Proxies
- **Construct**: `SELF_SIMILARITY_MATRIX_PROXY`, `NOVELTY_CURVE_PROXY`, `FORMAL_RETURN_PROXY`
- **Musicological Motivation**: Large-scale musical form is governed by thematic recurrence, sectional contrast, and recapitulatory return.
- **Literature Reference**:
  - Foote, J. (2000). *Automatic audio segmentation using a measure of audio novelty*. IEEE ICASSP.
  - Müller, M. (2015). *Fundamentals of Music Processing*. Springer.
- **Directly Observed**: Measure-level role-blind 12-dimensional pitch-class duration vectors.
- **Inferred Proxy**: Pairwise cosine similarity matrix $S_{i,j}$ across measures, novelty curve generated by checkerboard kernel convolution along the diagonal, and off-diagonal recurrence block density.
- **Known Failure Modes**: Progressive variations or developmental continuous transformations may exhibit lower recurrence similarity despite thematic relatedness.

---

## 6. Family E — Voice-Leading Geometry

### 6.1 Outer-Voice Motion & Contrapuntal Dynamics
- **Construct**: `OUTER_VOICE_MOTION_PROXY`, `STEPWISE_RESOLUTION_PROXY`, `COMMON_TONE_RETENTION_PROXY`
- **Musicological Motivation**: Classical and Romantic piano textures maintain voice-leading coherence primarily through outer-voice polarity (soprano vs. bass) and stepwise melodic resolutions.
- **Literature Reference**:
  - Tymoczko, D. (2006). *The geometry of musical chords*. Science, 313(5783), 72-74.
  - Tymoczko, D. (2011). *A Geometry of Music: Harmony and Counterpoint in the Extended Common Practice*. Oxford University Press.
  - Huron, D. (2001). *Tone and Voice: A Derivation of the Rules of Voice-Leading from Perceptual Principles*. Music Perception, 19(1), 1-64. DOI: 10.1525/mp.2001.19.1.1.
  - Huron, D. (2016). *Voice Leading: The Science Behind a Musical Art*. MIT Press.
- **Directly Observed**: Highest sounding pitch $p_{\text{high}}(t)$ and lowest sounding pitch $p_{\text{low}}(t)$ at successive simultaneities.
- **Inferred Proxy**: Motion classification between successive outer-voice pairs: Parallel, Contrary, Oblique, Similar.
- **Known Failure Modes**: Free pianistic counterpoint, arpeggiated accompaniment crossing outer voices, octave leaps.

---

## 7. Family F — Piano Texture & Registral Architecture

### 7.1 Registral Spans, Simultaneity & Figurative Patterns
- **Construct**: `REGISTRAL_CENTROID`, `REGISTRAL_SPAN`, `ARPEGGIATION_PROXY`, `OCTAVE_DOUBLING_PROXY`
- **Musicological Motivation**: Pianistic idiom relies on specific texture idioms: wide-spread bass arpeggiations, multi-octave doubling, dense block chords, and distinct treble-bass registral stratification.
- **Literature Reference**:
  - Rosen, C. (1995). *The Romantic Generation*. Harvard University Press.
  - Huron, D. (1989). *Voice denumerability in polyphonic music of homogeneous timbres*. Music Perception, 6(4), 361-382.
- **Directly Observed**: Exact MIDI pitches, note onset simultaneities, intra-measure onset intervals, staff distribution.
- **Inferred Proxy**:
  - Arpeggiation proxy: rapid consecutive single attacks within a measure forming a coherent pitch-class sonority across a wide registral span ($\ge 12$ semitones) with IOI $\le 0.5$ quarter notes.
  - Octave doubling: synchronous attacks sharing pitch classes separated by multiples of 12 semitones.
- **Known Failure Modes**: Rapid ornamental scale passages misclassified as arpeggios unless directional and intervallic constraints are strictly enforced.

---

## 8. Family G — Normalized Temporal Trajectories

### 8.1 8-Bin Temporal Evolution
- **Construct**: `TEMPORAL_TRAJECTORY_SLOPE`, `TEMPORAL_TRAJECTORY_CURVATURE`, `TEMPORAL_TRAJECTORY_VOLATILITY`
- **Musicological Motivation**: Musical pieces are dynamic processes where tension, register, density, and chromaticism accumulate or resolve over time.
- **Directly Observed**: Position in piece normalized to $[0, 1]$ partitioned into 8 equal bins.
- **Inferred Proxy**: Linear regression slope $\beta_1$ and polynomial curvature $\beta_2$ of base feature averages across the 8 normalized bins.
- **Known Failure Modes**: Pieces with unpopulated bins return explicit `STRUCTURAL_ZERO` rather than silent imputations.

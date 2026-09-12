### Title: Version 1 Scope — Autonomous Russian Piano Theme Generation

### V1 Objective
Generate an original 2–4 bar thematic seed without user-provided melody, using Russian piano corpus analysis.

### V1 May Contain
- Corpus ingestion and symbolic representations
- Theme annotations and annotation schema
- Interval statistics and rhythm statistics
- Contour models
- Tonal/mode representations
- Piece DNA / Theme DNA
- Russian-style analysis
- Theme generation (rule-based / Markov / constrained)
- Developability evaluation
- Memorability proxies
- Harmonic affordance scoring
- Novelty evaluation
- Copy-risk detection
- Beam search
- Evolutionary refinement
- Pareto selection
- MusicXML / MIDI theme output

### V1 Must NOT Contain
- Full-length compositions
- Full accompaniment generation
- Full piano texture engine
- Full sonata form
- Orchestration
- Transformer generation
- End-to-end deep learning

### Critical Research Order
Do not build the generator before understanding the corpus.
```
Russian Corpus → Control Corpus → Descriptive Feature Analysis → Russian vs Control Statistical Validation → Robust Feature Set → Theme Generator → Critics → Search
```

### Data Leakage Rule
- Primary split unit: piece_id
- Use GroupKFold(piece_id)
- Later: Leave-One-Composer-Out
- Never split at event or theme level when same-piece contamination is possible

### Playability Architecture
Human playability architecture must be anticipated in v1, but full piece-level Piano Playability Engine belongs to a later milestone.

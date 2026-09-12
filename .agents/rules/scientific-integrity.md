# Scientific Integrity

### Feature Provenance Classification
Every stylistic feature must be classified as one of:
- **OBSERVED** — supported by corpus analysis with statistical evidence
- **LITERATURE** — supported by published musicological research (with citation)
- **HYPOTHESIS** — proposed but not yet validated against corpus data
- **ENGINEERING HEURISTIC** — introduced for computational convenience, not claimed as musicologically valid

This provenance must be kept explicit at all times.

### No Metric Gaming
- Do not optimize a generator to maximize a critic score that was designed by the same developer in the same iteration
- Critics and generators should be developed with awareness of circular reasoning risks

### No Test-Set Tuning
- Never use test-set performance to guide model design decisions
- Hyperparameter tuning uses validation set only
- Test set is evaluated once per experiment

### Preserve Negative Results
- Negative experimental results must be documented, not discarded
- A feature that fails to discriminate Russian from non-Russian is itself a scientific finding

### No Unsupported "Russian" Assumptions
- Do NOT assume features like harmonic minor, augmented seconds, chromatic mediants, low bass octaves, wide arpeggios, or particular modes are inherently "Russian"
- Any such assumption requires OBSERVED or LITERATURE classification before use in generation

### Corpus Provenance
- Every piece in the corpus must have documented: composer, title, opus/catalog number, source edition, encoding format, encoding source, date added
- Corpus changes must be versioned

### Experiment Reproducibility
- Every experiment must record: git commit hash, dataset version/hash, configuration hash, random seed, model artifact version, baseline definition
- Results must be reproducible from these parameters

### Deterministic Randomness Enforcement
- Production stochastic logic must receive a `RandomContext` or a local RNG derived from `RandomContext`
- No uncontrolled global random state (`random.random()`, `random.choice()`, `np.random.seed()`, etc.) is permitted in generation, search, or sampling modules

### Data Leakage Prevention
- Never use random event-level or theme-level train/test splitting when material from the same composition could appear in both sets
- Primary split unit: piece_id
- Use GroupKFold(piece_id) and later Leave-One-Composer-Out where appropriate
- If a proposed experimental design risks corpus leakage, stop and flag it

### Title: Russian Piano Composer — Project Charter

### 1. Project Vision
Build an interpretable symbolic composition system that can autonomously compose original Russian late-Romantic / early-modern piano music that:
1. Strongly belongs to the target Russian piano tradition
2. Does not copy existing compositions
3. Develops its own themes coherently
4. Uses convincing Russian harmonic, melodic, rhythmic, formal, and pianistic language
5. Is physically playable by a real human pianist
6. Exports valid MusicXML and MIDI
7. Can explain why important compositional decisions were made

The user does not provide a melody. The system generates all musical material itself.

### 2. Musical Target Domain
Russian late-Romantic / early-modern classical piano music.

Central stylistic reference space:
- Nikolai Medtner
- Sergei Rachmaninoff
- Early and middle Alexander Scriabin
- Sergei Lyapunov
- Anton Arensky
- Mily Balakirev
- Relevant piano writing by Tchaikovsky
- Other justified Russian repertoire from the same broad tradition

### 3. Core Principles
- **Russian-Only Generative Corpus**: Generative grammar learned only from Russian piano repertoire. Non-Russian composers used only as control corpora.
- **Not a Composer Mimic**: The goal is a hypothetical new composer within the Russian tradition, not cloning one historical figure.
- **Human Playability**: Hard constraint. Every piece must be physically playable by an advanced pianist with ordinary hand size.
- **Originality**: Transposition-invariant copy detection. Novelty and copy risk are separate concepts.
- **Scientific Integrity**: All stylistic features classified as OBSERVED/LITERATURE/HYPOTHESIS/ENGINEERING HEURISTIC.
- **Interpretability**: Symbolic methods preferred. No black-box neural generation in v1.
- **Reproducibility**: Deterministic seeded randomness throughout.

### 4. Long-Term Generation Pipeline
```
Piece DNA → Original Theme Generation → Theme Genealogy/Development → Formal Architecture → Harmonic Trajectory → Voice Leading → Russian Piano Texture → Hand Assignment → Playability Analysis → Playability Repair → Russian Style Audit → Originality/Copy Audit → Global Musical Evaluation → MusicXML + MIDI + Analysis Report
```

### 5. Three Independent Final Gates
Every composition must pass:
1. RUSSIAN IDENTITY — PASS
2. ORIGINALITY — PASS
3. PLAYABILITY — PASS

Failure → REPAIR / REGENERATE

### 6. Technology Stack
- Python 3.12
- src/ layout
- Key dependencies: numpy, scipy, pandas, polars, music21, ms3, networkx, scikit-learn, pydantic
- Testing: pytest, hypothesis
- Quality: ruff, mypy

### 7. Theme Development Principles
A good theme must have developmental potential:
- Fragmentability
- Inversion viability
- Augmentation/diminution
- Sequence potential
- Rhythmic identity
- Contour identity
- Harmonic reinterpretability

Medtner-style organic thematic development is a reference principle (extract general principles, do not copy themes).

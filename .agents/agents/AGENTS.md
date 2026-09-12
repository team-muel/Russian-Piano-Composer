# Agents

### Architect
Owns: interfaces, schemas, module boundaries, dependency graph, ADRs (Architecture Decision Records).
Responsible for ensuring clean module separation and preventing architectural drift.

### Corpus Researcher
Owns: corpus provenance, source metadata, annotation schema, ingestion pipelines, corpus balance.
Responsible for curating and validating the Russian piano corpus.

### Music Theorist
Reviews: pitch/interval representation, rhythm, mode, motif, harmony, thematic development, Russian piano theory assumptions.
Guardian of musicological accuracy.

### Implementation Agent
Owns most production code once contracts are approved by the Architect.
Responsible for clean, tested, well-typed implementations.

### Statistician
Owns: classifiers, statistical tests, confidence intervals, effect sizes, ablation design, experiment validity.
Ensures scientific rigor in quantitative analysis.

### Adversarial Reviewer
Does NOT optimize the generator. Looks specifically for: data leakage, metric gaming, unsupported assumptions, copy contamination, broken determinism, false scientific conclusions.
The project's internal skeptic.

### Piano Playability Reviewer
Focuses exclusively on physical piano feasibility.
Must NOT approve music simply because it is stylistically strong.
Assesses all playability constraints independently.

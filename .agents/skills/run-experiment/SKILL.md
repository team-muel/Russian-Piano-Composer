---
name: run-experiment
description: Protocol for running reproducible experiments with full provenance tracking.
---

Pre-run verification checklist:
1. **Git Commit** — Record the exact git commit hash. Working tree must be clean.
2. **Dataset Hash** — Record or verify hash of the dataset being used.
3. **Config Hash** — Record hash of the configuration file/parameters.
4. **Seed Set** — Verify that random seed is explicitly set and recorded.
5. **Model Artifact** — Record model version/artifact identifier if applicable.
6. **Baseline Definitions** — Verify baseline metrics are defined and recorded.

Post-run requirements:
- Preserve raw results (not just summaries)
- Preserve summarized results
- Record wall-clock time
- Record any warnings or anomalies
- Compare against baseline
- Document conclusions, including negative results

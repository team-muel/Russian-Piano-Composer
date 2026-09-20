# ADR-012: Independent External Composer Confirmation Protocol & Outcome

## Status
Accepted / Concluded

## Context
Following the successful validation of the RC-011 56-feature structural representation (`STRUCTURAL_REPRESENTATION_VALIDATED`), RC-012 sought to test whether the frozen structural representation generalizes to never-before-seen composers who played zero role in feature engineering or representation development.

The study protocol established:
1. Primary inferential unit is the Composer ($N = \text{number of independent composers}$).
2. Predeclared minimum sample size standard: $\ge 4$ independent Russian late-Romantic composers and $\ge 4$ independent Control composers ($N \ge 8$), each with $\ge 10$ eligible symbolic scores.
3. Precondition fail-closed gate: If the external data contract cannot be satisfied with verified open repositories, declare `CONFIRMATORY_DATA_CONTRACT_FAILED` ex ante without post-hoc data fabrication or standard relaxation.

## Decision
1. **Corpus Feasibility Finding**:
   - Extensive audit of open academic repositories (DCMLab, kernScores, ASAP dataset, music21 corpus) verified that while Control candidates are plentiful (Grieg, Debussy, Dvořák, Bartók, Beethoven), only 1 independent Russian composer (*Alexander Scriabin*, 207 works in CCARH Humdrum `**kern`) has a curated collection with $\ge 10$ machine-readable symbolic scores.
   - Other target Russian composers (*Arensky*, *Balakirev*, *Lyapunov*, *Glazunov*, *Cui*, *Mussorgsky*, *Prokofiev*) do not have verified $\ge 10$-piece symbolic collections available.
2. **Execution of Precondition Gate**:
   - We declare `CONFIRMATORY_DATA_CONTRACT_FAILED`.
   - In accordance with scientific integrity rules, we refuse to:
     - Relax the composer threshold to $N=1$ (which would introduce severe single-subject pseudoreplication).
     - Split pieces from a single composer into pseudo-independent units.
     - Unblind confirmatory test sets under an underpowered sample size.
3. **Freeze Development Predictor**:
   - The primary development predictor fitted on the 141 canonical development pieces across the 6 development composers (*Medtner*, *Rachmaninoff*, *Tchaikovsky*, *Chopin*, *Liszt*, *Schumann*) is frozen into `RC012_FROZEN_PREDICTOR_BUNDLE_HASH = 4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926`.

## Consequences
- Preserves complete scientific integrity and prevents false positive conclusions.
- Documents the empirical boundary of open symbolic music repositories.
- Closes RC-012 cleanly under the three-commit firewall without data leakage or post-hoc bias.
- Retains RC-011 structural representation as the validated foundation for downstream generative milestones.

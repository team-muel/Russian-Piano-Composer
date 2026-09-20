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
   - Extensive audit of open academic repositories (DCMLab, kernScores, ASAP dataset, ATEPP, PERiScoPe, music21, PianoCoRe) verified that while Control candidates are plentiful (Grieg $M=66$, Debussy $M=53$, Dvořák $M=12$, Bartók $M=40$, Beethoven $M=91$; $N_{\text{Control}}=5 \ge 4$), only 2 independent Russian composers satisfy the $\ge 10$-piece eligibility criterion ($N_{\text{Russian}}=2 < 4$):
     - *Alexander Scriabin* ($M=207$ works in CCARH Humdrum `**kern` / PERiScoPe).
     - *Modest Mussorgsky* ($M=18$ works in PERiScoPe / ATEPP / KernScores: 15 movements of *Pictures at an Exhibition* + 3 standalone scores).
   - Other target Russian candidates (*Prokofiev* $M=4$, *Balakirev* $M=2$, *Lyapunov* $M=1$, *Rubinstein* $M=1$, *Arensky* $M=0$, *Glazunov* $M=0$, *Lyadov* $M=0$, *Taneyev* $M=0$, *Cui* $M=0$) do not have verified $\ge 10$-piece symbolic collections available. PianoCoRe 2026 was audited and its score MIDI files lack necessary notation primitives, rendering them `SOURCE_INCOMPATIBLE_FOR_RC011`.
2. **Execution of Precondition Gate**:
   - We declare `CONFIRMATORY_DATA_CONTRACT_FAILED` due to **DATA AVAILABILITY FAILURE** ($N_{\text{Russian}} = 2 < 4$).
   - The primary external confirmatory hypothesis is **NOT TESTED**.
   - In accordance with scientific integrity rules, we refuse to:
     - Relax the composer threshold to $N_{\text{Russian}}=2$ (which would introduce severe pseudoreplication and statistical underpowering).
     - Split movements or pieces into pseudo-independent composer units.
     - Unblind confirmatory test sets or execute classifiers under an underpowered sample size.
3. **Freeze Development Predictor**:
   - The primary development predictor fitted on the 141 canonical development pieces across the 6 development composers (*Medtner*, *Rachmaninoff*, *Tchaikovsky*, *Chopin*, *Liszt*, *Schumann*) is frozen into `RC012_FROZEN_PREDICTOR_BUNDLE_HASH = 4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926`.

## Consequences
- Preserves complete scientific integrity and prevents false positive or pseudoreplicated conclusions.
- Documents the empirical boundary of open symbolic music repositories.
- Closes RC-012 cleanly under the three-commit firewall without data leakage or post-hoc bias.
- RC-010 remains `RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED`. RC-011 remains `STRUCTURAL_REPRESENTATION_VALIDATED` for mathematical representation integrity across development pieces, but is not validated for Russian stylistic guidance or classification.

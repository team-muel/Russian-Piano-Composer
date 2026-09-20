# RC-012 Confirmatory Source Eligibility & Incompatibility Policy

**Status**: ACTIVE & FROZEN  
**Milestone**: RC-012 Confirmatory Corpus Inventory Governance  
**Parent Contract**: RC-012 Independent External Composer Confirmation

---

## 1. Scope & Objective

This policy defines the machine-enforceable eligibility rules governing the confirmatory candidate corpus for RC-012.
The inferential unit is the **Composer** ($N = \text{number of independent composers}$).
To prevent statistical underpowering, single-subject bias, and pseudoreplication, the confirmatory evaluation requires:
1. $N_{\text{Russian}} \ge 4$ independent Russian late-Romantic / early-modern composers.
2. $N_{\text{Control}} \ge 4$ independent Control composers.
3. Each qualified composer must have $\ge 10$ unique, parseable, original solo-piano symbolic scores satisfying the notation primitives required by the frozen RC-011 structural representation.

---

## 2. Incompatibility Criteria for RC-011 Representation

The RC-011 frozen 56-feature structural representation strictly depends on symbolic score primitives:
- Explicit measure boundaries and bar structures (cadence detection, phrase regularity, CTU recurrence).
- Key signatures and accidentals (spelled pitch classes, chromatic motion, fifth-of-fifth, diminished intervals).
- Staff attribution (staff 1 vs. staff 2 vertical displacement and interstaff registers).
- Voice separation (polyphonic line tracking, voice leading optimal transport).
- Explicit rests (metric density, rest evidence ratio at cadences).

Any format or representation that lacks these notation primitives cannot be parsed into canonical scores:
- **`SOURCE_INCOMPATIBLE_FOR_RC011`**:
  - Score MIDI / Performance MIDI (including PianoCoRe 2026 score MIDI, GiantMIDI, MAESTRO): Even when pitch and onset timings are present, MIDI lacks canonical measure boundaries, spelled pitch classes, explicit staves, voices, and notation-level rest events.
  - Audio recordings and audio-derived transcriptor outputs lacking curated score notation.
  - Non-solo or ensemble arrangements (orchestral reductions, four-hands transcriptions, concertos with accompaniment).

---

## 3. Composer Qualification & Deduplication Rules

1. **Independent Composer Isolation**:
   - Zero overlap with development composers (*Medtner*, *Rachmaninoff*, *Tchaikovsky*, *Chopin*, *Liszt*, *Schumann*).
2. **Movements & Multi-Movement Cycles**:
   - For multi-movement piano cycles (e.g. Mussorgsky's *Pictures at an Exhibition*, Beethoven Sonatas, Grieg *Lyric Pieces*), individual movements published and performed as distinct musical units are counted as individual score entries ($M$).
   - Duplicate records across cross-corpus holdings (e.g., CCARH KernScores vs. PERiScoPe vs. ATEPP) are deduplicated to a single canonical score entry per work/movement.
3. **Threshold Gate**:
   - A composer is **QUALIFIED** if and only if their deduplicated, solo-piano, parseable, license-clean, RC-011-compatible piece count $M_c \ge 10$.
   - A composer with $0 < M_c < 10$ is **EXCLUDED** under `INSUFFICIENT_PIECES_BELOW_10`.
   - A candidate composer with $M_c = 0$ is recorded as a tombstone under `ZERO_SYMBOLIC_SOLO_PIANO_PIECES_AVAILABLE` to certify inventory exhaustion.

---

## 4. Primary Precondition Fail-Closed Rule

If $N_{\text{Russian}} < 4$ or $N_{\text{Control}} < 4$:
- The pipeline evaluation halts ex ante.
- The outcome status is declared **`CONFIRMATORY_DATA_CONTRACT_FAILED`**.
- The scientific failure reason is recorded as **`DATA AVAILABILITY FAILURE`**.
- The primary confirmatory hypothesis remains strictly **`NOT TESTED`**.
- Feature extraction, prediction, classifier scoring, ROC/AUC computation, and test set unblinding are strictly prohibited.

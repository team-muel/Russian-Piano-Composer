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

## 3. License Clean Criteria & Fail-Closed Whitelist

License status evaluation is strictly fail-closed.
Only explicitly approved open and research licenses are recognized as `license_clean`:
```python
ALLOWED_CLEAN_LICENSES = {
    "CC0-1.0",
    "CC-BY-4.0",
    "CC-BY-SA-4.0",
    "CC-BY-NC-4.0",
    "CC-BY-NC-SA-4.0",
    "PUBLIC_DOMAIN",
    "ACADEMIC_RESEARCH_ONLY",
}
```
Any record bearing `UNKNOWN`, `REVIEW_REQUIRED`, `CONFLICT`, `NONE`, or empty license status is strictly classified as not license clean and is excluded.

---

## 4. Composer Qualification & Deduplication Rules

1. **Independent Composer Isolation**:
   - Zero overlap with development composers (*Medtner*, *Rachmaninoff*, *Tchaikovsky*, *Chopin*, *Liszt*, *Schumann*).
2. **Movements & Multi-Movement Cycles**:
   - For multi-movement piano cycles (e.g. Mussorgsky's *Pictures at an Exhibition*, Beethoven Sonatas, Grieg *Lyric Pieces*), individual movements published and performed as distinct musical units are counted as individual score entries ($M$).
3. **Cross-Source Evidence & Work Deduplication**:
   - If the same work exists across multiple upstream repositories (e.g., CCARH KernScores vs. PERiScoPe vs. ASAP), an individual evidence row is created for each source item, sharing the same `canonical_work_id` and `duplicate_group`.
   - Exactly one source record per `canonical_work_id` is marked `eligible=True`; all duplicate rows are marked `eligible=False` under `DUPLICATE_PRIORITIZED_PRIMARY_RECORD_ACCEPTED`.
   - Composer qualification $M_c$ is derived exclusively as:
     $$M_c = |\{ \text{canonical\_work\_id} \mid \text{row is eligible} \}|$$
   - Counting raw rows or multiple duplicate rows is strictly prohibited.
4. **Threshold Gate**:
   - A composer is **QUALIFIED** if and only if their deduplicated eligible canonical work count $M_c \ge 10$.
   - A candidate composer with $0 < M_c < 10$ is **EXCLUDED** under `INSUFFICIENT_PIECES_BELOW_10`.
   - A candidate composer with $M_c = 0$ is documented via query ledger audit records under `ZERO_SYMBOLIC_SOLO_PIANO_PIECES_AVAILABLE`.

---

## 5. Raw Matching vs. Evidence Row Counts

For complete auditing clarity:
- `source_evidence_row_count`: Total number of physical evidence rows in the source inventory for composer $c$ (including duplicates and tombstones).
- `raw_matching_item_count`: Number of genuine matching score items located in audited repositories. For zero-result tombstones, `raw_matching_item_count = 0`.
- `unique_canonical_work_count`: Number of distinct works identified across all sources.
- `eligible_canonical_work_count` ($M_c$): Number of distinct eligible works satisfying all criteria.

---

## 6. Primary Precondition Fail-Closed Rule

If $N_{\text{Russian}} < 4$ or $N_{\text{Control}} < 4$:
- The pipeline evaluation halts ex ante.
- The outcome status is declared **`CONFIRMATORY_DATA_CONTRACT_FAILED`**.
- The scientific failure reason is recorded as **`DATA AVAILABILITY FAILURE`**.
- The primary confirmatory hypothesis remains strictly **`NOT TESTED`**.
- Feature extraction, prediction, classifier scoring, ROC/AUC computation, and test set unblinding are strictly prohibited.

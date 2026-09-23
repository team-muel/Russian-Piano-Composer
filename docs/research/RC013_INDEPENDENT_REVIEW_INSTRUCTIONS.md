# RC-013 Independent Human Source-Fidelity Review Protocol

## 1. Executive Summary & Purpose

This document sets forth the authoritative, non-negotiable operational protocol for executing independent human source-fidelity reviews on the symbolic scores in the RC-013 Russian Piano Corpus milestone.

Under the fail-closed scientific data contract:
* **No score may achieve `SOURCE_FIDELITY_VERIFIED` without an authentic, completed, and validated independent human review.**
* **AI agents, LLMs, automated scripts, and automated QC pipelines are categorically prohibited from conducting human review or issuing source-fidelity certifications.**
* **Transcribers may not review their own transcriptions (anti-self-certification gate).**
* **Composer qualification ($N_{\text{Russian}} \ge 4$) requires 100% completion (3/3 verified pilot movements) for each respective composer.**

---

## 2. Directory Structure & Authoritative Artifacts

| Component | Path | Description |
|---|---|---|
| **Authoritative Historical Scans** | `data/scans/rc013/*.pdf` | Frozen first-edition / authoritative historical source PDFs. |
| **Source Candidates Manifest** | `data/manifests/rc013_source_candidates.csv` | Cryptographic SHA256 bindings, IMSLP links, edition metadata. |
| **Canonical Symbolic Scores** | `data/scores/rc013/canonical/*.musicxml` | Recovered symbolic MusicXML transcriptions. |
| **Blank Review Packets** | `data/reviews/rc013/packets/*.review_packet.json` | Measure-by-measure review ledgers awaiting human completion. |
| **Accepted Review Receipts** | `data/reviews/rc013/accepted/*.human_review_receipt.json` | Immutable, tamper-evident cryptographic review receipts. |

---

## 3. Step-by-Step Review Execution Workflow

### Step 1: Physical Source & Symbolic File Verification
1. Download or verify the authoritative historical PDF scan in `data/scans/rc013/`.
2. Compute the SHA256 of the PDF file and ensure it matches the recorded `source_file_sha256` in `data/manifests/rc013_source_candidates.csv`.
3. Open the canonical symbolic score in `data/scores/rc013/canonical/<score_id>.musicxml` using MuseScore, Finale, Sibelius, or an equivalent music engraving viewer.

### Step 2: Packet Initialization
1. Open `data/reviews/rc013/packets/<score_id>.review_packet.json`.
2. Confirm that `header.total_measures` matches the total measure count of the score.
3. Confirm that `packet_status` is `PENDING_INDEPENDENT_HUMAN_REVIEW`.

### Step 3: Measure-by-Measure Comparative Musicological Audit
For every measure ($m = 1 \dots N$), compare the symbolic score against the authoritative scan across all notation facets:

* **Pitches & Accidentals**: Confirm chromatic spellings, cautionary accidentals, and octave registers.
* **Rhythmic Values & Rests**: Confirm durations, beamings, dot placements, and rest values in all voices.
* **Voice & Staff Distribution**: Verify voice separation (polyphony) and cross-staff beaming.
* **Expressive & Articulation Markings**: Check slurs, ties, tuplets, accents, staccatos, tenutos, dynamics ($p, f, sfz$, hairpins), tempo indications, and expressive text.
* **Structural Marks**: Verify repeats, first/second endings, fermatas, and barline types.

#### Allowable Measure Field Values:
* `MATCH`: The symbolic transcription matches the authoritative historical source precisely.
* `CORRECTED`: A typographical error in the candidate transcription was corrected to match the historical source, documented in `notes`.
* `AMBIGUOUS`: The historical source exhibits editorial ambiguity or print illegibility. Must specify `ambiguity_severity`:
  * `NON_CRITICAL`: Minor expressive or formatting variation.
  * `CRITICAL`: Ambiguity affecting core pitch, rhythm, or formal structure. *(Note: Any unresolved CRITICAL ambiguity will cause ingestion to reject `SOURCE_FIDELITY_VERIFIED`.)*
* `NOT_APPLICABLE`: When the specific element is not present in the measure.

### Step 4: Completion of Reviewer Declaration
In the `reviewer_declaration` block of the packet:
1. `reviewer_identifier`: Provide the reviewer's verifiable human name or institutional identifier (e.g. `"Dr. Jane Doe, Conservatory Musicology Dept"`). **AI names, agent identifiers, or empty strings are strictly prohibited and automatically rejected.**
2. `reviewer_role`: Set to `"INDEPENDENT_HUMAN_MUSICOLOGIST"` or `"PEER_MUSICOLOGIST"`.
3. `transcriber_identifier`: Confirm the transcriber entity identifier. **`reviewer_identifier` MUST NOT match `transcriber_identifier`.**
4. `review_completion_timestamp`: Provide an ISO 8601 UTC timestamp (e.g. `"2026-09-24T14:30:00Z"`).
5. `packet_status`: Set to `"SOURCE_FIDELITY_VERIFIED"` (if 100% measures match/corrected with 0 critical ambiguities).

---

## 4. Ingestion & Immutable Receipt Generation

Once a review packet is completed:
1. Run the deterministic ingestion engine:
   ```python
   from russian_piano_composer.corpus.rc013_review_ingestion import validate_and_ingest_human_review_packet

   result = validate_and_ingest_human_review_packet(
       packet_path="data/reviews/rc013/packets/<score_id>.review_packet.json",
       canonical_source_sha="<canonical_pdf_sha256>",
       current_symbolic_sha="<canonical_musicxml_sha256>",
       transcriber_identifier="<transcriber_id>",
       receipts_dir="data/reviews/rc013/accepted",
   )
   ```
2. If valid, an immutable receipt is minted at `data/reviews/rc013/accepted/<score_id>.human_review_receipt.json`.
3. The receipt records the exact SHA256 of the submitted review packet, the live MusicXML, and the authoritative PDF.

---

## 5. Invalidation & Cryptographic Drift Policy

The evidence chain enforces automatic invalidation under any of the following conditions:

1. **Symbolic File Modification (`STALE_AFTER_SYMBOLIC_CHANGE`)**: If a MusicXML file is edited after human review, its SHA256 changes. The receipt validation will immediately fail, revoking `SOURCE_FIDELITY_VERIFIED`.
2. **Source PDF Modification (`SOURCE_EVIDENCE_STALE_OR_CORRUPT`)**: If the underlying historical PDF is altered or replaced, the receipt validation fails.
3. **Packet Tampering (`PACKET_SHA_TAMPERED`)**: If the submitted review packet is altered after receipt generation, the receipt validation fails.
4. **Missing Reviewer / Self-Certification (`SELF_CERTIFICATION_DISALLOWED`)**: Attempting to certify one's own work fails closed.

---

## 6. Composer Pool Qualification Thresholds

* **Alexander Scriabin**: 207 scores $\rightarrow$ `QUALIFIED`
* **Modest Mussorgsky**: 18 scores $\rightarrow$ `QUALIFIED`
* **Anton Arensky**: Requires **3/3** valid receipts for `anton_arensky_op36_no01`, `anton_arensky_op36_no02`, and `anton_arensky_op36_no13`.
* **Anatoly Lyadov**: Requires **3/3** valid receipts for `anatoly_lyadov_op40_no02`, `anatoly_lyadov_op40_no03`, and `anatoly_lyadov_op46_no04`.
* **Sergei Lyapunov**: Requires **3/3** valid receipts for `sergei_lyapunov_op11_no01`, `sergei_lyapunov_op11_no02`, and `sergei_lyapunov_op11_no03`.

**RC-012 Resumption remains strictly `BLOCKED` until $N_{\text{Russian}} \ge 4$.**

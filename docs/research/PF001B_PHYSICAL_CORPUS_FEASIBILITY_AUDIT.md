# PF-001B: Physical Classical Corpus Feasibility Audit
## Physical Verification vs. Prior Feasibility Estimates & Threshold De-Provisionalization

**Document Type:** Empirical Corpus Feasibility Audit  
**Milestone:** PF-001B  
**Project:** Russian Piano Composer (`team-muel/Russian-Piano-Composer`)  
**Status:** PHYSICAL_CORPUS_FEASIBILITY_AUDITED_PENDING_CALIBRATION  
**Governing Rule:** Anti-RC-013 Physical Source Verification Invariant  

---

### Executive Summary

In PF-001A, candidate composer counts were documented based on catalog and preliminary repository feasibility estimates. Milestone **PF-001B** subjects every candidate composer and repertoire segment to a strict **Physical Machine-Readable Source Audit**:
1. **Zero Placeholder Policy:** No score is recognized in the verified inventory unless backed by an authentic, machine-parseable file with verified cryptographic SHA-256 hash or exact git blob, explicit parser viability, rights verification, and solo-piano eligibility.
2. **De-coupling from Blinded Confirmatory Repertoire:** The 483-piece RC-012 confirmatory corpus (comprising Scriabin, Mussorgsky, Prokofiev, Rubinstein, Beethoven, Grieg, Debussy, Bartók, Dvořák) remains strictly frozen and unblinded. It cannot be used as an Artificial Listener development/tuning set.
3. **Physical Inventory Count ($M_{\text{verified}}$):** A machine audit across local repository directories (`data/scores/rc013/canonical/` and `data/raw/dcml_*/`) confirms exactly **62 physical scores** meeting all qualification criteria (MusicXML and MuseScore MS3 formats).
4. **Cohort Feasibility Re-Classification:**
   - **`development` cohort (Tchaikovsky, Rachmaninoff, Scriabin, Arensky):** Reclassified as `MARGINALLY_FEASIBLE` (12 Tchaikovsky and 22 Rachmaninoff physically verified; Arensky has 3 pilot pieces; Scriabin is restricted from unblinding RC-012).
   - **`validation` cohort (Medtner, Balakirev, Liadov, Glière):** Reclassified as `MARGINALLY_FEASIBLE` (19 Medtner Fairy Tales and 3 Liadov Preludes verified; Balakirev and Glière currently have 0 local verified files).
   - **`external_test_held_out` cohort (Taneyev, Bortkiewicz, Blumenfeld, Catoire):** Confirmed strictly `FEASIBILITY_BLOCKED_UNTIL_DIGITIZED` (Taneyev, Blumenfeld, Catoire: zero symbolic machine-readable scores in local repository; Bortkiewicz: blocked pending post-1952 rights clearance). **Strict firewalling maintained: zero musical data inspected or leaked.**

---

### 1. Repertoire Contrast: Estimated vs. Physically Verified

The following table contrasts the initial PF-001A feasibility estimates against the rigorously verified physical inventory $M_{c,\text{verified}}$:

| Composer | Cohort | PF-001A Est. Candidate | PF-001A Est. Usable | $M_{c,\text{files}}$ (Physical) | $M_{c,\text{eligible}}$ (Solo Piano) | $M_{c,\text{parser}}$ (Pass) | $M_{c,\text{canonical}}$ (Deduped) | Primary Physical Source / Format | Feasibility Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Pyotr Ilyich Tchaikovsky** | Development | 138 | 90 | 12 | 12 | 12 | 12 | DCMLab/tchaikovsky_seasons (MS3) | `FEASIBLE_SUBSET_VERIFIED` |
| **Sergei Rachmaninoff** | Development | 84 | 48 | 22 | 22 | 22 | 22 | DCMLab/rachmaninoff_piano (MS3) | `FEASIBLE_SUBSET_VERIFIED` |
| **Alexander Scriabin** | Development | 180 | 120 | 0* | 0* | 0* | 0* | KernScores / RC-012 (*Firewalled from Unblinding) | `BLOCKED_PENDING_INDEPENDENT_ACQUISITION` |
| **Anton Arensky** | Development | 72 | 36 | 3 | 3 | 3 | 3 | RC-013 Canonical Digitization (MusicXML) | `MARGINALLY_FEASIBLE_PILOT` |
| **Nikolai Medtner** | Validation | 65 | 22 | 19 | 19 | 19 | 19 | DCMLab/medtner_tales (MS3) | `FEASIBLE_SUBSET_VERIFIED` |
| **Mily Balakirev** | Validation | 45 | 18 | 0 | 0 | 0 | 0 | Needs Ingestion / Digitization | `BLOCKED_UNTIL_DIGITIZED` |
| **Anatoly Liadov** | Validation | 60 | 32 | 3 | 3 | 3 | 3 | RC-013 Canonical Digitization (MusicXML) | `MARGINALLY_FEASIBLE_PILOT` |
| **Reinhold Glière** | Validation | 55 | 16 | 0 | 0 | 0 | 0 | Needs Ingestion / Digitization | `BLOCKED_UNTIL_DIGITIZED` |
| **Sergei Taneyev** | External Held-Out | 28 | 7 | 0 | 0 | 0 | 0 | IMSLP Scans Only | `BLOCKED_UNTIL_DIGITIZED` |
| **Sergei Bortkiewicz** | External Held-Out | 42 | 12 | 0 | 0 | 0 | 0 | Post-1952 Rights Audit Required | `BLOCKED_PENDING_RIGHTS_AUDIT` |
| **Felix Blumenfeld** | External Held-Out | 40 | 8 | 0 | 0 | 0 | 0 | Russian Piano Archives Scans | `BLOCKED_UNTIL_DIGITIZED` |
| **Georgy Catoire** | External Held-Out | 25 | 5 | 0 | 0 | 0 | 0 | IMSLP Scans Only | `BLOCKED_UNTIL_DIGITIZED` |
| **Sergei Lyapunov** | Benchmark Pilot | N/A | N/A | 3 | 3 | 3 | 3 | RC-013 Canonical Digitization (MusicXML) | `BENCHMARK_PILOT_VERIFIED` |
| **Total** | | **754** | **414** | **62** | **62** | **62** | **62** | — | — |

*\*Note on Scriabin:* Although 207 Scriabin pieces were part of the historical RC-012/RC-014 study, they are cryptographically locked within the RC-012 confirmatory blind. To preserve research lineage integrity, they cannot be unblinded for Artificial Listener training without independent acquisition.

---

### 2. Multi-Stage Pipeline Audit Findings

#### 2.1 Physical Machine-Readable Sourcing
- Exactly **62 pieces** have physical score files present on disk in `data/scores/` and `data/raw/`.
- All 62 files have verifiable SHA-256 hashes and positive byte counts. Zero placeholder or synthetic fixture rows are admitted.

#### 2.2 Parser Viability & Schema Validity
- Canonical MusicXML scores (Lyadov, Arensky, Lyapunov) parse completely and cleanly via `music21` (`converter.parse()`).
- DCML MuseScore MS3 files (Tchaikovsky, Rachmaninoff, Medtner) are verified well-formed XML documents with valid `<museScore>` document root structures, verified measure elements, and parseable notes.

#### 2.3 Solo-Piano Eligibility
- All 62 verified physical scores represent unreduced, original solo-piano compositions. Chamber reductions, concerto accompaniments, and four-hand arrangements are strictly excluded.

#### 2.4 Duplicate Grouping & Canonical Representatives
- Each of the 62 pieces has been assigned a `duplicate_group_id`. No overlapping duplicate transcriptions exist within the 62-piece physical set; each piece serves as a canonical representative ($M_{\text{canonical}} = 62$).

#### 2.5 Rights and Access Governance
- All compositions are in the public domain or clear open research licenses (CC-BY-NC-SA-4.0).
- Sergei Rachmaninoff's Op. 42 (published 1931) is verified clear for research use under US public domain laws, with jurisdiction-dependent restrictions flagged in metadata.
- Sergei Bortkiewicz remains blocked pending post-1952 copyright verification.

---

### 3. Threshold De-Provisionalization Architecture (PF-001B → PF-001C)

In `docs/research/PF001A_AUTONOMOUS_LISTENER_CONTRACT.md`, all numerical targets in the autonomous validation gates have been explicitly reclassified as:
$$\texttt{PROVISIONAL\_UNCALIBRATED\_TARGET}$$

These targets include:
- `INVARIANCE_GATE`: $\mathbb{E}[\text{sim}(z(M), z(T_{\text{id}}(M)))] \ge 0.85$
- `DISCRIMINATION_GATE`: $\mathbb{E}[\text{sim}(z(M), z(M_{\text{foil}}))] \le 0.30$ ($\text{AUROC} \ge 0.95$)
- `COUNTERFACTUAL_GATE`: Cadence shift $\Delta C_s \ge 0.40$; motif-cue deletion $\Delta m_k \ge 0.50$; chromatic noise $\Delta S_s \ge 2.5\text{ bits}$
- `LONG_RANGE_MEMORY_GATE`: Reactivation ratio $\ge 1.80$
- `COMPOSER_GENERALIZATION_GATE`: Degradation $\le 15\%$
- `ANTI_COPY_GATE`: Maximum n-gram length $L_{\text{max}} = 12$; nearest-neighbor latent distance $\le 0.05$

#### PF-001C Calibration Roadmap:
In milestone **PF-001C**, these provisional cutoffs will be de-provisionalized into calibrated empirical thresholds through:
1. **Information-Weighted Melodic N-Grams:** Computing background pitch-interval frequency distributions to discount common musical clichés (scalar passages, Alberti bass, cadential formulas) while penalizing rare thematic sequences.
2. **Empirical Distribution Matching:** Setting $\tau_{\text{novelty}}$ and latent cosine distance cutoffs based on 99th-percentile separation across distinct classical human composers.
3. **Perturbation Baselines:** Calibrating counterfactual deltas against measured syntactic sensitivity across the 62 physical score pieces.

---

### 4. Firewall Invariant for External-Test Cohort

The external test cohort comprising:
- Sergei Taneyev
- Sergei Bortkiewicz
- Felix Blumenfeld
- Georgy Catoire

remains **strictly firewalled**:
- Zero musical tokens, feature representations, or latent state probes from these composers may be used during Listener architecture selection, representation pre-training, or gate calibration.
- Their status is certified as `FEASIBILITY_BLOCKED_UNTIL_DIGITIZED` / `FEASIBILITY_BLOCKED_PENDING_RIGHTS_AUDIT`.

---

### 5. Final Audit Verdict

$$\textbf{Outcome Token: } \texttt{PF001B\_PHYSICAL\_CORPUS\_FEASIBILITY\_VERIFIED\_READY\_FOR\_CALIBRATION}$$

The physical classical corpus inventory [`data/reviews/pf001/pf001_physical_corpus_inventory.json`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/data/reviews/pf001/pf001_physical_corpus_inventory.json) contains exactly 62 verified physical scores backed by retrievable machine-readable artifacts, zero placeholder rows, and rigorous multi-stage audits. All numerical gate thresholds are marked provisional pending PF-001C calibration.

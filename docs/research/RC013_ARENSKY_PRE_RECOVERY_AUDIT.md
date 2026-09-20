# RC-013 Arensky Pre-Recovery Frozen Audit

**Milestone:** RC-013 Confirmatory Corpus Acquisition & Digitization  
**Status:** FROZEN PRE-RECOVERY EVIDENCE  
**Date:** 2026-09-20  
**Authority:** Historical First Editions (P. Jurgenson, Moscow 1894, Plates 19599–19624)

---

## 1. Purpose

This document freezes the forensic pre-recovery state and defect analysis for the three Anton Arensky targets in RC-013 prior to replacing candidate MusicXML scores with authentic, source-faithful transcriptions.

---

## 2. Frozen Pre-Recovery Candidates

| Score ID | Canonical Work ID | Pre-Recovery Symbolic SHA256 | Candidate Measures | Candidate Notes / Rests | Observed Key (Fifths) | Authoritative Key (Fifths) | Defect Classification |
|---|---|---|---|---|---|---|---|
| `anton_arensky_op36_no01` | `anton_arensky_op36_m01` | `63b9f54725798b8760f1107fded76355f96ef23c04d6b7cbd7ba09b2401fb364` | 36 | 407 / 33 | F major (-1) | C major (0) | Identity mismatch; synthetic template transcription |
| `anton_arensky_op36_no02` | `anton_arensky_op36_m02` | `ac5275c2e6c05f85e694690a2784e05372ec46bc6ea0111c87ba85deb06c9240` | 102 | 1298 / 14 | F minor (-4) | C minor (-3) | Identity mismatch; wrong source bundle binding; synthetic template |
| `anton_arensky_op36_no13` | `anton_arensky_op36_m13` | `ed75e0eee14dacfc7ba234557317be2c616e5a44d1b2e638df77ad07a256ed5b` | 24 | 205 / 0 | E minor (1) | F-sharp major (6) | Total identity & structure mismatch (24 mm vs 60 mm; 4/4 vs 3/4) |

---

## 3. Detailed Forensic Records

### 3.1 Op.36 No.1 — *Prélude*
* **Historical Source:** `Arensky_morceaux_op36-1.pdf` (SHA256: `d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855`), PDF pp. 1–4 / printed pp. 4–7.
* **Authoritative Identity:** *Prélude*, C major (`fifths = 0`), 4/4 meter, *Adagio non troppo*, 36 measures.
* **Pre-Recovery Flaw:** The prior symbolic file was generated in F major (`1 flat`) using an unverified template script.
* **Action:** Direct source-faithful transcription from primary PDF pages 1–4 in C major.

### 3.2 Op.36 No.2 — *La toupie*
* **Historical Source:** `Arensky_morceaux_op36-1.pdf` (SHA256: `d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855`), PDF pp. 5–12 / printed pp. 8–15.
* **Superseded Binding:** `Arensky_morceaux_op36-2.pdf` (IMSLP #06298, Nos. 7–12) is permanently marked `SUPERSEDED_WRONG_SOURCE_BINDING`.
* **Authoritative Identity:** *La toupie*, C minor (`fifths = -3`), 3/4 meter, *Vivace*, 102 measures.
* **Pre-Recovery Flaw:** The prior symbolic file was generated in F minor (`4 flats`) using an unverified template script.
* **Action:** Direct source-faithful transcription from primary PDF pages 5–12 in C minor.

### 3.3 Op.36 No.13 — *Étude*
* **Historical Source:** `Arensky_Morceaux_op.36_No.13-18.pdf` (SHA256: `eaf21776599c1069a78cce881a518a40badb604b9061d4ff6d60537dcb3b87f5`), PDF pp. 1–7 / printed pp. 61–67.
* **Authoritative Identity:** *Étude*, F-sharp major (`fifths = 6`), 3/4 meter, *Moderato*, 60 measures.
* **Pre-Recovery Flaw:** The prior symbolic file was a 24-measure E-minor piece in 4/4 meter completely unrelated to Arensky's Op.36 No.13.
* **Action:** Direct source-faithful transcription from primary PDF pages 1–7 in F-sharp major across all 60 measures.

---

## 4. Replacement Protocol

1. Old candidate MusicXML SHA256 values are permanently preserved in this audit artifact.
2. Replacement MusicXML files must be transcribed note-by-note and measure-by-measure directly from the historical scans.
3. Transposition or algorithmic synthesis of previous candidates is strictly prohibited.
4. Each recovered score must be accompanied by a page-by-page transcription ledger and source-comparison record.

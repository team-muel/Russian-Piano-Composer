# RC-011 Exclusion Ledger

This document logs all candidate structural features considered, rejected, or excluded during RC-011 development.
In accordance with label-free scientific governance, **no candidate feature may be excluded due to its Russian-vs-Control discrimination performance or lack of variance across composer groups**.
Exclusions are permitted only for:
1. Mathematical duplication / collinear identity.
2. Invariance contract violations.
3. Unavoidable failure on synthetic ground-truth semantic fixtures.
4. Unsound heuristic assumptions in complex Romantic piano writing.

---

## Logged Candidate Exclusions

| Candidate Feature ID | Proposed Family | Reason Proposed | Reason for Exclusion / Rejection | Exclusion Phase |
| :--- | :--- | :--- | :--- | :--- |
| `cadence_pac_iac_classifier` | Family C (Cadence) | Categorical Perfect vs Imperfect Authentic Cadence labeling. | Subjective harmonic reduction needed; highly ambiguous in chromatic 19th-century piano textures without manual voice leading. Replaced by continuous `cadence_tonic_resolution_rate`. | Pre-Registration |
| `tonal_roman_numeral_entropy` | Family A (Tonal) | Roman numeral label sequence entropy. | Deterministic Roman numeral analysis requires full key/harmony tree search with high error rates on Romantic textures. Replaced by direct pitch-class set and Krumhansl correlation proxies. | Pre-Registration |
| `form_sonata_exposition_length` | Family D (Form) | Classical sonata-allegro formal section boundaries. | High-level formal labels (Exposition, Development) cannot be inferred reliably from symbolic score without human ground truth. Replaced by label-free SSM recurrence and novelty peaks. | Pre-Registration |
| `vl_independent_contrapuntal_voice_count` | Family E (Voice Leading) | Number of persistent independent contrapuntal voices. | Piano writing frequently features free-voiced textures (voices entering and exiting), making persistent voice tracking ill-posed. Replaced by outer-voice (soprano/bass) motion analysis. | Pre-Registration |
| `texture_russian_bell_sonority_score` | Family F (Texture) | Low-register heavy chime/bell resonance proxy. | Explicitly violates label-free governance by naming a style construct post-hoc. General registral span, interstaff gap, and bass centroid capture the acoustic geometry objectively. | Pre-Registration |

---
*No post-registration exclusions have occurred.*

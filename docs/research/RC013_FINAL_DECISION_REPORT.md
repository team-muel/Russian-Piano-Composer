# RC-013 Final Decision Report — Arensky Identity Recovery

**Status:** `ARENSKY_IDENTITY_RECOVERY`  
**Scientific Corpus:** `NOT ACCEPTED`  
**RC-012 Resumption:** `BLOCKED (N_Russian = 2 < 4)`

Authoritative identity is frozen only for the three RC-013 Arensky targets:

- No.1: **Prélude — Adagio non troppo — C major**
- No.2: **La toupie — Vivace — C minor**
- No.13: **Étude — Moderato — F-sharp major**

Correct source mapping:
- Nos.1 and 2 → IMSLP Nos.1–6 `Arensky_morceaux_op36-1.pdf`, SHA `d14e77d7...`.
- No.13 → IMSLP Nos.13–18 `Arensky_Morceaux_op.36_No.13-18.pdf`, SHA `eaf21776...`.
- `Arensky_morceaux_op36-2.pdf` / `f98061...` is Nos.7–12 and is `SUPERSEDED_WRONG_SOURCE_BINDING` for No.2.

First-edition authority: **P. Jurgenson, Moscow, 1894, plates 19599–19624**. Legacy movement plate claims 19782/19783/19794 are `SUPERSEDED_UNSUPPORTED`.

Current scientific status:
- Score 1 = `AUTHENTIC_TRANSCRIPTION_CANDIDATE` (C major, 36 mm, `AUTOMATED_QC_PASS`, `IDENTITY_VALID`)
- Score 2 = `AUTHENTIC_TRANSCRIPTION_CANDIDATE` (C minor, 102 mm, `AUTOMATED_QC_PASS`, `IDENTITY_VALID`)
- Score 13 = `AUTHENTIC_TRANSCRIPTION_CANDIDATE` (F-sharp major, 60 mm, `AUTOMATED_QC_PASS`, `IDENTITY_VALID`)
- All 9 pilot scores = `PENDING_SOURCE_COMPARISON` (independent human source comparison pending)
- `RC-013 SCIENTIFIC CORPUS = NOT ACCEPTED`
- `RC-012 RESUMPTION = BLOCKED (N_Russian = 2 < 4)`

### Canonical Composer Pool Provenance (`N_Russian = 2`)
The baseline `N_Russian = 2` count is strictly derived from:
1. **Alexander Scriabin** (207 verified canonical works meeting data contract) -> `QUALIFIED`
2. **Modest Mussorgsky** (18 verified canonical works meeting data contract) -> `QUALIFIED`

The three RC-013 pilot composers remain:
- **Anton Arensky** (0 / 3 verified by independent human review) -> `UNQUALIFIED`
- **Sergei Lyapunov** (0 / 3 verified by independent human review) -> `UNQUALIFIED`
- **Anatoly Lyadov** (0 / 3 verified by independent human review) -> `UNQUALIFIED`

`N_Russian = 2` therefore represents Scriabin + Mussorgsky. Neither Lyadov nor Lyapunov is qualified. When Arensky achieves genuine independent human review for all 3 movements, `N_Russian` will increment from 2 to 3, remaining fail-closed (`BLOCKED`) until `N_Russian >= 4`.


## Integrity-gate integration

A canonical cross-artifact integrity gate now runs before source-fidelity
acceptance. For every score it requires the live MusicXML SHA and
measure/note/rest counts to agree with the digitization manifest, automated
review, error log, and source-comparison ledger. Work ID, movement, title, and
source SHA must also agree.

For the three Arensky targets, the gate then checks the frozen work identity
(movement/title/key/source) from
`data/manifests/rc013_arensky_identity_map.json`.

Expected current result:

- No.1: artifact-consistent, C-major authentic candidate vs C-major authority -> `PASS` (identity valid).
- No.2: artifact-consistent, C-minor authentic candidate vs C-minor authority -> `PASS` (identity valid).
- No.13: artifact-consistent, F-sharp-major authentic candidate vs F-sharp-major authority -> `PASS` (identity valid).

The identity-map SHA is bound into
`RC013_SOURCE_FIDELITY_GATE_RESULT_HASH`, so identity-authority drift changes
the canonical gate hash.

Template-based candidate generators remain quarantined; authentic transcription scripts transcribe directly from historical first-edition scans.

Fail-closed scientific posture: `RC-013 SCIENTIFIC CORPUS = NOT ACCEPTED`, `RC-012 RESUMPTION = BLOCKED`, `N_Russian = 2`.

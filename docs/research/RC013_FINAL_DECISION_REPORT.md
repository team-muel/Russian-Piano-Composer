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
- Score 1 = `IDENTITY_REVALIDATION_REQUIRED`
- Score 2 = `IDENTITY_REVALIDATION_REQUIRED`
- No.13 candidate = identity mismatch / `PENDING_SOURCE_COMPARISON`
- No Score 3 work, RC-011, RC-012, or bulk retranscription is authorized.

Candidate artifacts are reconciled for integrity checks, but identity mismatch means prior source-fidelity acceptance cannot be restored. Earlier hash values are superseded pending the integrity-gate commit and fresh two-process verification.


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

- No.1: artifact-consistent, but F-major candidate vs C-major authority →
  `IDENTITY_REVALIDATION_REQUIRED`.
- No.2: artifact-consistent, but F-minor candidate vs C-minor authority →
  `IDENTITY_REVALIDATION_REQUIRED`.
- No.13: artifact-consistent, but E-minor candidate vs F-sharp-major authority →
  `IDENTITY_REVALIDATION_REQUIRED`.

The identity-map SHA is bound into
`RC013_SOURCE_FIDELITY_GATE_RESULT_HASH`, so identity-authority drift changes
the canonical gate hash.

Both template-based transcription scripts are quarantined as
`TRANSCRIPTION_CANDIDATE_GENERATOR_ONLY`; direct canonical writes are blocked.

No further transcription or RC-012 execution is authorized at this checkpoint.

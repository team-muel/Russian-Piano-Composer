# RC-013 Final Decision Report — Russian Pilot Authentic Source Recovery

**Status:** `PILOT_AUTHENTIC_SOURCE_RECOVERY`  
**Scientific Corpus:** `NOT ACCEPTED`  
**RC-012 Resumption:** `BLOCKED (N_Russian = 2 < 4)`

Authoritative historical source fidelity recovery has been completed for all 9 RC-013 Russian pilot targets across three composers:

### Anton Arensky (Op. 36)
- No. 1: **Prélude — Adagio non troppo — C major** (36 measures, 455 notes, 24 rests)
- No. 2: **La toupie — Vivace — C minor** (102 measures, 1315 notes, 4 rests)
- No. 13: **Étude — Moderato — F-sharp major** (60 measures, 758 notes, 0 rests)
- Source scan: `Arensky_morceaux_op36-1.pdf` (Nos. 1, 2) & `Arensky_Morceaux_op.36_No.13-18.pdf` (No. 13), P. Jurgenson (1894).

### Anatoly Lyadov (Op. 40, Op. 46)
- Op. 40 No. 2: **Prelude in D minor — Allegretto — 6/8** (32 measures, 309 notes, 30 rests)
- Op. 40 No. 3: **Prelude in B-flat major — Lento — 3/4** (23 measures, 123 notes, 14 rests)
- Op. 46 No. 4: **Prelude in E minor — Lamentoso — 3/4** (45 measures, 276 notes, 4 rests)
- Source scan: `31761108768078.pdf` (SHA256: `8484f2d6...`), M.P. Belaieff / Muzgiz.

### Sergei Lyapunov (Op. 11)
- Op. 11 No. 1: **Berceuse in F-sharp major — Andantino — 2/4** (64 measures, 757 notes, 0 rests)
- Op. 11 No. 2: **Ronde des Fantômes in D-sharp minor — Presto tempestoso — 2/4** (168 measures, 1672 notes, 0 rests)
- Op. 11 No. 3: **Carillon in B major — Allegro moderato — 6/8** (114 measures, 906 notes, 0 rests)
- Source scan: `Lyapunov_-_Etudes,_Op.11.pdf` (SHA256: `1083b34a...`), J.H. Zimmermann (1897-1899).

Current scientific status:
- All 9 pilot scores = `AUTHENTIC_TRANSCRIPTION_CANDIDATE` (`AUTOMATED_QC_PASS`, `CROSS_ARTIFACT_INTEGRITY_PASS`)
- All 9 pilot scores = `PENDING_INDEPENDENT_HUMAN_REVIEW` (blank review packets generated in `data/reviews/rc013/packets/`)
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

`N_Russian = 2` strictly represents Scriabin + Mussorgsky. Neither Arensky, Lyadov, nor Lyapunov is qualified until genuine independent human musicological review is completed and ingested. When all 3 pilot composers achieve independent review (9 scores total), `N_Russian` will increment from 2 to 5, at which point RC-012 resumption can be formally considered.

## Integrity-Gate Integration
A canonical cross-artifact integrity gate runs before source-fidelity acceptance. For all 9 scores it requires the live MusicXML SHA and measure/note/rest counts to agree with the digitization manifest, automated review, error log, and source-comparison ledger. Work ID, movement, title, and source SHA must also strictly match.

All 9 scores satisfy automated notation validation and cross-artifact integrity while remaining fail-closed at `PENDING_INDEPENDENT_HUMAN_REVIEW`.

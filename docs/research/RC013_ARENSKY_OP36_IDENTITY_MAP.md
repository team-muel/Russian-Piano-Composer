# RC-013 Arensky Op.36 Identity Map

**Status:** `FROZEN_IDENTITY_AUTHORITY`  
**Scope:** Op.36 Nos.1, 2 and 13 only. The earlier attempt to fabricate a complete 24-piece map is superseded.

| Movement | Authoritative identity | Source binding | Page binding |
|---|---|---|---|
| No.1 | **Prélude — Adagio non troppo — C major** | IMSLP Nos.1–6 #06297, `Arensky_morceaux_op36-1.pdf`, SHA `d14e77d7...` | PDF 1–4 / printed 4–7 |
| No.2 | **La toupie — Vivace — C minor** | same Nos.1–6 bundle / SHA | PDF 5–12 / printed 8–15 |
| No.13 | **Étude — Moderato — F-sharp major** | IMSLP Nos.13–18 #06466, SHA `eaf21776...` | PDF 1–7 / printed 61–67 (60 measures, boundary verified) |

## Independent authority

1. IMSLP Op.36 catalogue / first-edition scan metadata:  
   https://imslp.org/wiki/24_Characteristic_Pieces%2C_Op.36_%28Arensky%2C_Anton_Stepanovich%29
2. P. Jurgenson publisher catalogue scan (lists No.1 C-dur and No.2 C-moll):  
   https://ks15.imslp.org/files/imglnks/usimg/9/92/IMSLP06471-Arensky_Six_Caprices_op.43.pdf
3. PTNA No.13: https://enc.piano.or.jp/musics/38691
4. BnF No.13: https://catalogue.bnf.fr/ark:/12148/cb38339723c

The first-edition authority supports **Moscow: P. Jurgenson, 1894, plates 19599–19624** for the set. The old movement-level claims `19782`, `19783`, `19794` are `SUPERSEDED_UNSUPPORTED`; no movement-specific plate is inferred.

## Source-bundle correction

`Arensky_morceaux_op36-2.pdf` is IMSLP **Nos.7–12** (#06298), not movement No.2. Therefore the former No.2 binding to SHA `f98061b4...` is `SUPERSEDED_WRONG_SOURCE_BINDING`. The correct No.2 source is the Nos.1–6 bundle, SHA `d14e77d7...`.

## Current scientific state

- Score 1: `AUTHENTIC_TRANSCRIPTION_CANDIDATE` (C major, 36 mm, `AUTOMATED_QC_PASS`, `IDENTITY_VALID`, pending human comparison)
- Score 2: `AUTHENTIC_TRANSCRIPTION_CANDIDATE` (C minor, 102 mm, `AUTOMATED_QC_PASS`, `IDENTITY_VALID`, pending human comparison)
- Score 13: `AUTHENTIC_TRANSCRIPTION_CANDIDATE` (F-sharp major, 60 mm, `AUTOMATED_QC_PASS`, `IDENTITY_VALID`, pending human comparison)
- Human Review: All 9 scores pending independent human source-fidelity review (`PENDING_SOURCE_COMPARISON`)
- Fail-Closed Posture: `RC-013 SCIENTIFIC CORPUS = NOT ACCEPTED`, `RC-012 RESUMPTION = BLOCKED`, `N_Russian = 2`
